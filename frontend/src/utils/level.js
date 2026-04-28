export function parseLevel(levelValue = 0) {
  const normalizedLevel = Math.max(0, Math.min(Number(levelValue) || 0, 125))
  const crowns = Math.floor(normalizedLevel / 125)
  const remainAfterCrowns = normalizedLevel % 125
  const suns = Math.floor(remainAfterCrowns / 25)
  const remainAfterSuns = remainAfterCrowns % 25
  const moons = Math.floor(remainAfterSuns / 5)
  const stars = remainAfterSuns % 5

  if (crowns > 0) {
    return { icon: '👑', label: '王冠', count: crowns, levelValue: normalizedLevel }
  }
  if (suns > 0) {
    return { icon: '☀️', label: '太阳', count: suns, levelValue: normalizedLevel }
  }
  if (moons > 0) {
    return { icon: '🌙', label: '月亮', count: moons, levelValue: normalizedLevel }
  }
  if (stars > 0) {
    return { icon: '⭐', label: '星星', count: stars, levelValue: normalizedLevel }
  }

  return { icon: '', label: '基础态', count: 0, levelValue: normalizedLevel }
}
