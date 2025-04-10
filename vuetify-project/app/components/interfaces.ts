export interface PlotData {
    description: string,
    plotType: string,
    displayName: string
}
export interface ExtractorData {
    value: string,
    date: string
}
export interface ByExtractor {
    KClause: ExtractorData,
    KConfigReader: ExtractorData
}
export interface ScatterData {
    currentValue: {
        value: string,
        date: string
    }
}
