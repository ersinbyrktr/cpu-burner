import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 100,         // number of concurrent virtual users
  duration: '1200s', // total test duration
};

export default function () {
  const duration = 1; // seconds per request
  const threads = 8;
  const url = `http://34.32.89.225/cpu?duration=${duration}&threads=${threads}`;

  let res = http.get(url);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1); // pace each VU slightly
}
