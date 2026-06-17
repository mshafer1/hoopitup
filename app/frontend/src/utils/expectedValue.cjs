function computeExpectedValue(votes) {
  if (!votes || typeof votes !== "object") {
    throw new TypeError("votes must be an object");
  }

  const yes = Number(votes.yes || 0);
  const yes_if_3 = Number(votes.yes_if_3 || 0);
  const yes_if_5 = Number(votes.yes_if_5 || 0);
  const maybe = Number(votes.maybe || 0);

  var straight_count = votes.value.yes + Math.floor(0.5 * votes.value.maybe);
  var yes_if_3_count = votes.value.yes_if_3 + straight_count;
  var yes_if_5_count = votes.value.yes_if_5 + straight_count;

  console.log("Calculating expected game status with counts:", {
    straight_count,
    yes_if_3_count,
    yes_if_5_count,
  });

  if (yes_if_5_count >= 10) {
    return "5v5";
  } else if (yes_if_3_count >= 8) {
    return "4v4";
  } else if (yes_if_3_count >= 6) {
    return "3v3";
  } else if (straight_count >= 4) {
    return "2v2";
  } else {
    return `No game yet (${straight_count} total)`;
  }
}

module.exports = { computeExpectedValue };
