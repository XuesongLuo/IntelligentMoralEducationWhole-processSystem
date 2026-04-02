export function parseLevel(totalMonths = 0) {
  const maxMonths = 625 // 5王冠 = 5*5*5*5
  const months = Math.min(totalMonths, maxMonths)

  const crown = Math.floor(months / 125)
  const remainAfterCrown = months % 125

  const sun = Math.floor(remainAfterCrown / 25)
  const remainAfterSun = remainAfterCrown % 25

  const moon = Math.floor(remainAfterSun / 5)
  const star = remainAfterSun % 5

  return {
    crown,
    sun,
    moon,
    star
  }
}