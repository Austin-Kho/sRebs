INSERT INTO todo(`title`, `content`, `status`, `created`, `updated`) VALUES
('MySQL의 Docker 이미지를 만들기','MySQL의 Master, Slave 각각 사용할 수 있도록 환경변수 역할을 제어할 수 있는 MySQL 이미지를 만들기', 'DONE', NOW(), NOW()),
('MySQL의 Stack 구축','MySQL의 Master, Slave 각각의 Service에서 이루어진 스택으로 Swarm 클러스터 구축', 'DONE', NOW(), NOW()),
('API 구현','Go 언어에서 TODO 참조 · 갱신 처리를 위한 API를 구현', 'PROGRESS', NOW(), NOW()),
('Nginx의 Docker 이미지를 만들기','백엔드에 HTTP 요청을 흘리는 Nginx의 이미지를 만들기', 'PROGRESS', NOW(), NOW()),
('API의 Stack 구축','Nginx와 API로 이루어진 스택을 Swarm 클러스터 구축', 'PROGRESS', NOW(), NOW()),
('Web을 구현','Nuxt.js를 사용하여 API와 연계한 TODO 상태를 표시하는 Web 어플리케이션을 구현하기', 'PROGRESS', NOW(), NOW()),
('Web의 Stack 구축','Nginx와 Web 갖춰진 스택을 Swarm 클러스터 구축', 'PROGRESS', NOW(), NOW()),
('Ingress 구축','Swarm 클러스터 외부에서 액세스 할 수있는 Ingress 구축', 'TODO', NOW(), NOW());
