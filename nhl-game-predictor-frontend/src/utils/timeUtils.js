import { format, toZonedTime } from "date-fns-tz";

const PACIFIC_TZ = "America/Los_Angeles";

/**
 * converts a typical JavaScript Date object to PST and formats it to the specified
 * format. by default, the Django REST API expects dates in the format "yyyy-MM-dd"
 *
 * @param {string | Date} date - the input date
 * @param {string} dateFormat - output format, e.g., "yyyy-MM-dd HH:mm:ss"
 * @returns {string} - date string in PST
 */
const formatToPacificTime = (date, dateFormat = "yyyy-MM-dd") => {
  const pacificDate = toZonedTime(date, PACIFIC_TZ);
  return format(pacificDate, dateFormat, { timeZone: PACIFIC_TZ });
};

export default formatToPacificTime;
