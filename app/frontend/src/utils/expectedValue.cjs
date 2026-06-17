function computeExpectedValue(votes) {
  if (!votes || typeof votes !== "object") {
    throw new TypeError("votes must be an object");
  }

  const yes = Number(votes.yes || 0);
  const yes_if_3 = Number(votes.yes_if_3 || 0);
  const yes_if_5 = Number(votes.yes_if_5 || 0);
  const maybe = Number(votes.maybe || 0);

  let straight_count = yes + Math.floor(0.5 * maybe);

  var fives_counted = false;
  if (straight_count + yes_if_5 >= 10) {
    straight_count += yes_if_5;
    fives_counted = true;
  }
  if (straight_count + yes_if_3 >= 6) {
    straight_count += yes_if_3;
  } else if (straight_count + yes_if_3 + yes_if_5 >= 10 && !fives_counted) {
    straight_count += yes_if_3 + yes_if_5;
  }

  if (straight_count >= 10) {
    return "5v5";
  } else if (straight_count >= 8) {
    return "4v4";
  } else if (straight_count >= 6) {
    return "3v3";
  } else if (straight_count >= 4) {
    return "2v2";
  } else {
    return `No game yet (${straight_count} total)`;
  }
}

module.exports = { computeExpectedValue };
