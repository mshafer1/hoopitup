module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.cjs$': 'babel-jest'
  },
  testMatch: ['**/__tests__/**/*.test.cjs']
}
