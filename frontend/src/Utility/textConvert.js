export function textConvert(text) {
    return String(text)
        .replace(/([A-Z])/g, ' $1')
        .replace(/([a-z])([0-9])/g, '$1 $2')
        .trim()
        .toLowerCase()
        .replace(/^./, s => s.toUpperCase())
        .replace(/(\.\s+[a-z])/g, s => s.toUpperCase());
}