import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // ramp up
    { duration: '3m', target: 20 },   // steady load
    { duration: '30s', target: 0 },   // ramp down
  ],
  // The test FAILS if the service breaks its SLOs under load.
  thresholds: {
    http_req_failed: ['rate<0.005'],      // 99.5% availability
    http_req_duration: ['p(95)<300'],     // p95 under 300ms
  },
};

export default function () {
  const create = http.post(
    `${BASE_URL}/orders`,
    JSON.stringify({ item: 'widget', quantity: Math.ceil(Math.random() * 5) }),
    { headers: { 'Content-Type': 'application/json' } },
  );
  check(create, { 'create is 201': (r) => r.status === 201 });

  const list = http.get(`${BASE_URL}/orders`);
  check(list, { 'list is 200': (r) => r.status === 200 });

  sleep(0.5);
}
