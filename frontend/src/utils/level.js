function repeatIcons(icon, count, label) {
  return Array.from({ length: count }, () => ({ icon, label }))
}

export function parseLevel(levelValue = 0) {
  const normalizedLevel = Math.max(0, Math.min(Number(levelValue) || 0, 125))
  const crowns = Math.floor(normalizedLevel / 125)
  const remainAfterCrowns = normalizedLevel % 125
  const suns = Math.floor(remainAfterCrowns / 25)
  const remainAfterSuns = remainAfterCrowns % 25
  const moons = Math.floor(remainAfterSuns / 5)
  const stars = remainAfterSuns % 5

  const icons = [
    ...repeatIcons('👑', crowns, '王冠'),
    ...repeatIcons('☀️', suns, '太阳'),
    ...repeatIcons('🌙', moons, '月亮'),
    ...repeatIcons('⭐', stars, '星星')
  ]

  return {
    label: icons.length ? icons[0].label : '基础态',
    icons,
    levelValue: normalizedLevel
  }
}
