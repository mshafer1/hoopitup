const { computeExpectedValue } = require("../utils/expectedValue.cjs");

describe("computeExpectedValue (votes)", () => {
  test("returns no game yet when under thresholds", () => {
    // 1 + 2/2 = 2; yes_if_5_count = 4 + 2 = 6 -> not 5v5
    expect(computeExpectedValue({ yes: 1, maybe: 2, yes_if_5: 4 })).toBe(
      "No game yet (2 total)",
    );
    expect(computeExpectedValue({ yes: 1, maybe: 1 })).toBe(
      "No game yet (1 total)",
    );
    expect(computeExpectedValue({ yes: 3, maybe: 1 })).toBe(
      "No game yet (3 total)",
    );
  });

  test("returns 2v2 when 4<= straight_count < 6", () => {
    expect(computeExpectedValue({ yes: 2, maybe: 4 })).toBe("2v2");
    expect(computeExpectedValue({ yes: 4, maybe: 1 })).toBe("2v2");
    expect(computeExpectedValue({ yes: 4, maybe: 2 })).toBe("2v2");
    expect(computeExpectedValue({ yes: 3, maybe: 2 })).toBe("2v2");
    expect(computeExpectedValue({ yes: 0, maybe: 8 })).toBe("2v2");
    expect(computeExpectedValue({ yes: 0, maybe: 9 })).toBe("2v2");
  });

  test("returns 3v3 when yes_if_3_count >= 6", () => {
    expect(computeExpectedValue({ yes_if_3: 6 })).toBe("3v3");
    expect(computeExpectedValue({ yes_if_3: 7 })).toBe("3v3");
    expect(computeExpectedValue({ yes: 2, yes_if_3: 4 })).toBe("3v3");
    expect(computeExpectedValue({ yes: 1, maybe: 2, yes_if_3: 4 })).toBe("3v3");
  });

  test("returns 4v4 when at least 8", () => {
    expect(computeExpectedValue({ yes_if_3: 8 })).toBe("4v4");
    expect(computeExpectedValue({ yes_if_3: 9 })).toBe("4v4");
    expect(computeExpectedValue({ yes: 8 })).toBe("4v4");
    expect(computeExpectedValue({ yes: 2, yes_if_3: 6 })).toBe("4v4");
    expect(computeExpectedValue({ yes: 1, maybe: 4, yes_if_3: 5 })).toBe("4v4");
  });

  
  test("returns 5v5 when at least 10", () => {
    expect(computeExpectedValue({ yes_if_3: 10 })).toBe("5v5");
    expect(computeExpectedValue({ yes: 10 })).toBe("5v5");
    expect(computeExpectedValue({ yes: 5, yes_if_3: 5 })).toBe("5v5");
    expect(computeExpectedValue({ yes: 5, yes_if_5: 5 })).toBe("5v5");
  });

  test("returns no game when yes_if_5_count < 10", () => {
    const votes = { yes: 0, maybe: 0, yes_if_5: 8 };
    expect(computeExpectedValue(votes)).toBe("No game yet (0 total)");
  });

  test("throws when input is not an object", () => {
    expect(() => computeExpectedValue(null)).toThrow(TypeError);
  });
});
