import http from "k6/http";
import { check, sleep } from "k6";
import { Counter, Rate } from "k6/metrics";
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

// Счетчик запросов
export let all_requests = new Counter("http_requests");
// Показатель успешных запросов
export let success_rate = new Rate("http_requests_success");

// Опции для теста нагрузки
export let options = {
  stages: [
    { duration: "3m", target: 50 }, // Постепенное увеличение до 50 пользователей за 2 минуты
    { duration: "5m", target: 50 }, // Поддержание 50 пользователей в течение 6 минут
    { duration: "2m", target: 0 }, // Постепенное уменьшение до 0 пользователей за 2 минуты
  ],
};

// Основная функция, выполняемая каждым виртуальным пользователем
export default function () {
  // Генерируем случайное число от 0 до 1
  let random = Math.random();
  let userPayload = {
    username: `user_${__VU}_${__ITER}`,
    name: "Gena Boolkin",
    birthdate: "2024-04-24",
  };

  // С вероятностью 5% не включаем пароль в запрос
  if (random > 0.05) {
    userPayload.password = "qwerty123";
  }

  // Регистрация пользователя
  let register_response = http.post(
    "http://demo_service:8000/user-register",
    JSON.stringify(userPayload),
    { headers: { "Content-Type": "application/json" } },
  );

  // Проверка, что регистрация прошла успешно (статус 200)
  check(register_response, {
    "register status was 200": (r) => r.status === 200,
  });

  // Если регистрация успешна, получить пользователя по ID
  if (register_response.status === 200) {
    let user_id = register_response.json().uid;
    let get_user_by_id_response = http.post(
      `http://demo_service:8000/user-get?id=${user_id}`,
      null,
      {
        auth: `user_${__VU}_${__ITER}:qwerty123`,
      },
    );

    // Проверка, что запрос на получение пользователя по ID успешен (статус 200)
    check(get_user_by_id_response, {
      "get user by ID status was 200": (r) => r.status === 200,
    });

    // Получение пользователя по имени пользователя
    let get_user_by_username_response = http.post(
      `http://demo_service:8000/user-get?username=user_${__VU}_${__ITER}`,
      null,
      {
        auth: `user_${__VU}_${__ITER}:qwerty123`,
      },
    );

    // Проверка, что запрос на получение пользователя по имени пользователя успешен (статус 200)
    check(get_user_by_username_response, {
      "get user by username status was 200": (r) => r.status === 200,
    });

    // Повышение пользователя до администратора
    let promote_user_response = http.post(
      `http://demo_service:8000/user-promote?id=${user_id}`,
      null,
      {
        auth: `admin:superSecretAdminPassword123`,
      },
    );

    // Проверка, что запрос на повышение пользователя успешен (статус 200)
    check(promote_user_response, {
      "promote user status was 200": (r) => r.status === 200,
    });
  }

  // Увеличение счетчика запросов
  all_requests.add(1);
  // Добавление результата успешности запроса в показатель успешных запросов
  success_rate.add(register_response.status === 200);

  sleep(1);
}

// Функция для создания отчета
export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: " ", enableColors: true }),
    "/results/summary.json": JSON.stringify(data),
    "/results/report.html": htmlReport(data),
  };
}
