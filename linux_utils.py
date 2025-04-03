import re

def jaccard(a, b):
    return len(set.intersection(a, b)) / len(set.union(a, b))

def add_features(descriptor, source, features, min=2):
    descriptor[f'#{source}'] = len(features) if features is not None and len(features) >= min else np.nan

def get_variables(variable_map):
    variables = set(variable_map.values())
    if len(variables) <= 1:
        variables = set()
    return variables

def read_unconstrained_feature_variables(extractor, revision, architecture, output_directory):
    unconstrained_features_filename = f'{output_directory}/unconstrained-features/{extractor}/linux/{revision}[{architecture}].unconstrained.features'
    unconstrained_feature_variables = set()
    if os.path.isfile(unconstrained_features_filename):
        with open(unconstrained_features_filename, 'r') as f:
            unconstrained_feature_variables = set([re.sub('^CONFIG_', '', f.strip()) for f in f.readlines()])
    return unconstrained_feature_variables

def inspect_architecture_features_for_model(extractor, revision, architecture, config_features, features_for_last_revision,output_directory):
    global potential_misses_grep, potential_misses_kmax
    
    features_filename = f'{output_directory}/kconfig/{extractor}/linux/{revision}[{architecture}].features'
    with open(features_filename, 'r') as f:
        extracted_features = set([re.sub('^CONFIG_', '', f.strip()) for f in f.readlines()])
    
    unconstrained_feature_variables = read_unconstrained_feature_variables(extractor, revision, architecture)

    dimacs_filename = f'{output_directory}/backbone-dimacs/{extractor}/linux/{revision}[{architecture}].backbone.dimacs'
    all_variables = set()
    variables = set()
    feature_variables = set()
    core_feature_variables = set()
    dead_feature_variables = set()
    undead_feature_variables = set()
    all_feature_variables = set()
    features = set()
    core_features = set()
    unconstrained_features = set()
    constrained_features = set()
    added_features = None
    removed_features = None
    infos = {'extracted_features_jaccard': np.nan, \
                     'all_variables_jaccard': np.nan, \
                     'variables_jaccard': np.nan, \
                     'feature_variables_jaccard': np.nan, \
                     'undead_feature_variables_jaccard': np.nan, \
                     'all_feature_variables_jaccard': np.nan, \
                     'features_jaccard': np.nan, \
                     'unconstrained_bools': np.nan, \
                     'unconstrained_tristates': np.nan}
    
    if os.path.isfile(dimacs_filename):
        with open(dimacs_filename, 'r') as f:
            lines = f.readlines()
            all_variable_map = {}
            variable_map = {}
            feature_variable_map = {}
            for f in lines:
                if f.startswith('c '):
                    result = re.search('^c ([^ ]+) ([^ ]+)$', f)
                    if result:
                        index = int(result.group(1).strip())
                        name = result.group(2).strip()
                        all_variable_map[index] = name
                        if "k!" not in name:
                            variable_map[index] = name
                            if name != 'True' \
                                and name != '<unsupported>' \
                                and name != 'PREDICATE_Compare' \
                                and not name.startswith('__VISIBILITY__CONFIG_') \
                                and not name.endswith('_MODULE'):
                                feature_variable_map[index] = name
            all_variables = get_variables(all_variable_map)
            variables = get_variables(variable_map)
            feature_variables = get_variables(feature_variable_map)

            backbone_features_filename = f'{output_directory}/backbone-features/{extractor}/linux/{revision}[{architecture}].backbone.features'
            if os.path.isfile(backbone_features_filename):
                with open(backbone_features_filename, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        core_feature_variables = set([line[1:].strip() for line in lines if line.startswith('+')]).intersection(feature_variables)
                        dead_feature_variables = set([line[1:].strip() for line in lines if line.startswith('-')]).intersection(feature_variables)

            if len(feature_variables) > 0:
                undead_feature_variables = feature_variables.difference(dead_feature_variables)
                all_feature_variables = undead_feature_variables.union(unconstrained_feature_variables)
                features = all_feature_variables.intersection(config_features)
                if f'{revision}###{architecture}' not in extractor_comparison:
                    extractor_comparison[f'{revision}###{architecture}'] = features
                else:
                    extractor_comparison[f'{revision}###{architecture}'] = jaccard(extractor_comparison[f'{revision}###{architecture}'], features)
                core_features = features.intersection(core_feature_variables)
                unconstrained_features = features.intersection(unconstrained_feature_variables)
                unconstrained_features_by_type = pd.DataFrame(list(unconstrained_features), columns=['config']) \
                    .merge(df_config_types[(df_config_types['revision'] == revision)])
                unconstrained_bools = unconstrained_features_by_type[unconstrained_features_by_type['type'] == 'bool']['config'].drop_duplicates()
                unconstrained_tristates = unconstrained_features_by_type[unconstrained_features_by_type['type'] == 'tristate']['config'].drop_duplicates()
                constrained_features = features.difference(core_feature_variables).difference(unconstrained_feature_variables)
                if architecture in features_for_last_revision and len(features_for_last_revision[architecture]) > 0:
                    added_features = features.difference(features_for_last_revision[architecture])
                    removed_features = features_for_last_revision[architecture].difference(features)
                infos = { \
                            'extracted_features_jaccard': jaccard(extracted_features, features), \
                            'all_variables_jaccard': jaccard(all_variables, features), \
                            'variables_jaccard': jaccard(variables, features), \
                            'feature_variables_jaccard': jaccard(feature_variables, features), \
                            'undead_feature_variables_jaccard': jaccard(undead_feature_variables, features), \
                            'all_feature_variables_jaccard': jaccard(all_feature_variables, features), \
                            'features_jaccard': 1, \
                            'unconstrained_bools': len(unconstrained_bools), \
                            'unconstrained_tristates': len(unconstrained_tristates) \
                        }
    descriptor = {'extractor': extractor, 'revision': revision, 'architecture': architecture} | infos
    add_features(descriptor, 'config_features', config_features) # F_config
    add_features(descriptor, 'extracted_features', extracted_features) # F_extracted
    add_features(descriptor, 'unconstrained_feature_variables', unconstrained_feature_variables, min=1) # F_unconstrained
    add_features(descriptor, 'all_variables', all_variables) # V_all
    add_features(descriptor, 'variables', variables) # V_phi
    add_features(descriptor, 'feature_variables', feature_variables) # FV_phi
    add_features(descriptor, 'core_feature_variables', core_feature_variables, min=1) # FV_core
    add_features(descriptor, 'dead_feature_variables', dead_feature_variables, min=1) # FV_dead
    add_features(descriptor, 'constrained_feature_variables', undead_feature_variables.difference(core_feature_variables)) # FV_constrained
    add_features(descriptor, 'undead_feature_variables', undead_feature_variables) # FV_undead
    add_features(descriptor, 'all_feature_variables', all_feature_variables) # FV
    add_features(descriptor, 'ALL_feature_variables', feature_variables.union(unconstrained_feature_variables)) # FV_all
    add_features(descriptor, 'features', features) # F
    add_features(descriptor, 'core_features', core_features, min=1)
    add_features(descriptor, 'unconstrained_features', unconstrained_features, min=1)
    add_features(descriptor, 'constrained_features', constrained_features)
    add_features(descriptor, 'added_features', added_features, min=0)
    add_features(descriptor, 'removed_features', removed_features, min=0)
    if extractor == 'kmax':
        potential_misses_grep.update([f for f in all_feature_variables.difference(features) if '__CONFIG_' not in f])
    return descriptor, feature_variables.union(unconstrained_feature_variables), features

def inspect_architecture_features_for_revision(extractor, revision, features_for_last_revision):
    config_features = set(df_configs[df_configs['revision'] == revision]['config'])
    architectures = [re.search('\[(.*)\]', f).group(1) for f in glob.glob(f'{output_directory}/kconfig/{extractor}/linux/{revision}[*.features')]
    architectures = list(set(architectures))
    architectures.sort()
    data = []
    total_features = set()
    total_feature_variables = set()
    features_for_current_revision = {}
    for architecture in architectures:
        descriptor, feature_variables, features = inspect_architecture_features_for_model(extractor, revision, architecture, config_features, features_for_last_revision)
        data.append(descriptor)
        total_features.update(features)
        features_for_current_revision[architecture] = features
        if extractor == 'kmax':
            total_feature_variables.update(feature_variables)
    for descriptor in data:
        add_features(descriptor, 'total_features', total_features)
        total_added_features = None
        total_removed_features = None
        if 'TOTAL' in features_for_last_revision and len(features_for_last_revision['TOTAL']) > 0:
            total_added_features = total_features.difference(features_for_last_revision['TOTAL'])
            total_removed_features = features_for_last_revision['TOTAL'].difference(total_features)
        add_features(descriptor, 'total_added_features', total_added_features, min=0)
        add_features(descriptor, 'total_removed_features', total_removed_features, min=0)
    features_for_current_revision['TOTAL'] = total_features
    df_configs_configurable.loc[(df_configs_configurable['revision'] == revision) & (df_configs_configurable['config'].isin(total_features)), 'configurable'] = True
    if extractor == 'kmax':
        potential_misses_kmax.update([f for f in config_features.difference(total_feature_variables)])
    return data, features_for_current_revision

def inspect_architecture_features(extractor):
    print(f'{extractor} ', end='')
    revisions = [re.search('/linux/(.*)\[', f).group(1) for f in glob.glob(f'{output_directory}/kconfig/{extractor}/linux/*.features')]
    revisions = list(set(revisions))
    revisions.sort(key=Version)
    data = []
    features_for_last_revision = {}
    i = 0
    for revision in revisions:
        i += 1
        if i % 10 == 0:
            print(revision + ' . ', end='')
        new_data, features_for_last_revision = inspect_architecture_features_for_revision(extractor, revision, features_for_last_revision)
        data += new_data
    print()
    return data

if os.path.isfile(f'{output_directory}/linux-features.dat'):
    with open(f'{output_directory}/linux-features.dat', 'rb') as f:
        [features_by_kind_per_architecture, df_extractor_comparison, potential_misses_grep, potential_misses_kmax, df_configs_configurable] = pickle.load(f)
else:
    features_by_kind_per_architecture = inspect_architecture_features('kconfigreader')
    features_by_kind_per_architecture += inspect_architecture_features('kmax')
    features_by_kind_per_architecture = pd.DataFrame(features_by_kind_per_architecture)
    df_extractor_comparison = []
    for key, value in extractor_comparison.items():
        [revision, architecture] = key.split('###')
        if type(value) is set:
            value = pd.NA
        df_extractor_comparison.append({'revision': revision, 'architecture': architecture, 'extractor_jaccard': value})
    df_extractor_comparison = pd.DataFrame(df_extractor_comparison)
    with open(f'{output_directory}/linux-features.dat', 'wb') as f:
        pickle.dump([features_by_kind_per_architecture, df_extractor_comparison, potential_misses_grep, potential_misses_kmax, df_configs_configurable], f)

replace_values(features_by_kind_per_architecture)
df_features = pd.merge(df_architectures, features_by_kind_per_architecture, how='outer').sort_values(by='committer_date')
df_features = pd.merge(df_kconfig, df_features, how='outer').sort_values(by='committer_date')

def compare_with_grep(message, list):
    print(f'{message}: ' + str(len(list)))
    print(pd.merge(df_configs[['config','kconfig-file']], pd.DataFrame(list, columns=['config']), how='inner') \
        .drop_duplicates().merge(df_config_types[['config', 'type']]).drop_duplicates())

def report_potential_misses(potential_misses_grep, potential_misses_kmax):
    # these are the features NOT found by grep, but found by kmax (this allows us to check whether the grep regex matches too much)
    # the only matches are enviroment variables (e.g., ARCH) and mistakes in kconfig files: IA64_SGI_UV (which has a trailing `) and SND_SOC_UX500_MACH_MOP500 (which has a leading +)
    compare_with_grep('#potential misses (grep)', potential_misses_grep)
    print()

    # these are the features found by grep, but NOT found by kmax, either constrained or unconstrained (this allows us to check whether kmax matches enough)
    # as there are some extraction failures for kmax, we expect some misses; also, we do not extract the um architecture; and finally, there are some test kconfig files that are never included
    # in the following, we try to filter out these effects (this is not perfect though)
    potential_misses_kmax_with_type = (pd.merge(df_configs[['config','kconfig-file', 'revision']], pd.DataFrame(potential_misses_kmax, columns=['config']), how='inner') \
            .drop_duplicates().merge(df_config_types[['config', 'type']]).drop_duplicates())
    misses_due_to_tests = set(potential_misses_kmax_with_type[ \
            potential_misses_kmax_with_type['kconfig-file'].str.startswith('Documentation/') | \
            potential_misses_kmax_with_type['kconfig-file'].str.startswith('scripts/')]['config'].unique())
    missing_kmax_models = df_features[(df_features['extractor'] == 'KClause') & df_features['#extracted_features'].isna()]
    missing_kmax_models = missing_kmax_models[['revision', 'architecture']].drop_duplicates()
    potential_misses_kmax_with_type['architecture'] = potential_misses_kmax_with_type['kconfig-file'].apply(lambda s: re.sub(r'^arch/(.*?)/.*$', r'\1', s))
    potential_misses_due_to_missing_kmax_models = set(potential_misses_kmax_with_type.merge(missing_kmax_models[['revision', 'architecture']].drop_duplicates()) \
                                                    .drop(columns=['kconfig-file', 'revision', 'architecture', 'type'])['config'].unique())
    potential_misses_kmax = potential_misses_kmax.difference(misses_due_to_tests).difference(potential_misses_due_to_missing_kmax_models)
    # the remaining matches are due to our way of using kmax extractor, where we ignore lines with new kconfig constructs like $(success,...)
    compare_with_grep('#potential misses (kmax)', potential_misses_kmax)

report_potential_misses(potential_misses_grep, potential_misses_kmax)