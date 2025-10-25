# Hentikan dan hapus container
docker stop pubsub-aggregator
docker rm pubsub-aggregator

# Bersihkan database & event log
Remove-Item -Recurse -Force .\data\*

pip uninstall -y -r requirements.txt

Hal Pertama adalah melakukan build image

docker build -t uts-aggregator .

Kemudian kita jalankan dockernya

docker run -d --name pubsub-aggregator -p 8080:8080 -v ${PWD}/data:/app/data uts-aggregator

Kita cek apakah sudah berjalan

docker logs -f pubsub-aggregator

kita cek health nya
Invoke-RestMethod -Uri http://localhost:8080/health

kita cek rootnya
Invoke-RestMethod -Uri http://localhost:8080

baru mari kita cek statnya terlebih dahulu
Invoke-RestMethod -Uri http://localhost:8080/stats


Selanjutnya kita akan coba kirim 3 event
Event 1 dan 2 itu sama id nya 

$body1 = '{
  "topic": "user.login",
  "event_id": "evt1",
  "timestamp": "2025-10-25T12:30:00",
  "source": "duplicate_test",
  "payload": {
    "msg": "User Masuk"
  }
}'
Invoke-RestMethod -Uri http://localhost:8080/publish -Method Post -ContentType "application/json" -Body $body1

$body2 = '{
  "topic": "user.login",
  "event_id": "evt1",
  "timestamp": "2025-10-25T12:30:00",
  "source": "duplicate_test",
  "payload": {
    "msg": "User Masuk"
  }
}'
Invoke-RestMethod -Uri http://localhost:8080/publish -Method Post -ContentType "application/json" -Body $body2


dan untuk Event ke 3 kita buat berbeda

$body3 = '{
  "topic": "user.logout",
  "event_id": "evt2",
  "timestamp": "2025-10-25T12:30:00",
  "source": "duplicate_test",
  "payload": {
    "msg": "User Keluar"
  }
}'
Invoke-RestMethod -Uri http://localhost:8080/publish -Method Post -ContentType "application/json" -Body $body3

kita tunggu 3 detik dulu

Start-Sleep -Seconds 3
docker logs pubsub-aggregator --tail 20

Invoke-RestMethod -Uri http://localhost:8080/stats

kemudian kita akan untuk events

Invoke-RestMethod -Uri http://localhost:8080/events


Terus misal kita coba cari topik tentang user.login
Invoke-RestMethod -Uri http://localhost:8080/events?topic=user.login

maka dia akan mendapatkan user login sesuai yang sudah dimasukkan

begitu pula dengan ketika kita cari topik tentang user.logout
Invoke-RestMethod -Uri http://localhost:8080/events?topic=user.logout


Setelahnya kita coba untuk restart untuk mencek apakah ia masih menyimpan data sebelumnya
docker stop pubsub-aggregator
docker start pubsub-aggregator

Start-Sleep -Seconds 3

docker logs pubsub-aggregator --tail 10

kemudian jika kita cek statnya

Invoke-RestMethod -Uri http://localhost:8080/stats

kemudian kita tes untuk duplicate lagi

$body1 = '{
  "topic": "user.login",
  "event_id": "evt1",
  "timestamp": "2025-10-25T12:30:00",
  "source": "duplicate_test",
  "payload": {
    "msg": "User Masuk"
  }
}'
Invoke-RestMethod -Uri http://localhost:8080/publish -Method Post -ContentType "application/json" -Body $body1

Start-Sleep -Seconds 3

docker logs pubsub-aggregator --tail 5

lalu kita cek stats nya

Invoke-RestMethod -Uri http://localhost:8080/stats

kemudian kita cek events

Invoke-RestMethod -Uri http://localhost:8080/events

Selanjutnya saya akan menjalankan docker-compose, jadi akan saya hapus dulu docker container nya

docker stop pubsub-aggregator
docker rm pubsub-aggregator

kita up kan dulu

docker-compose up -d

kita cek dia berjalan di port 8080

docker-compose ps

kita cek lognya

docker-compose logs uts_aggregator

kita cek healthnya juga

Invoke-RestMethod -Uri http://localhost:8080/health


kita coba event yang baru dengan

$testEvent = '{
  "topic": "compose.test",
  "event_id": "evt1_compose",
  "timestamp": "2025-10-25T12:30:00",
  "source": "compose_demo",
  "payload": {
    "msg": "docker_compose"
  }
}'
Invoke-RestMethod -Uri http://localhost:8080/publish -Method Post -ContentType "application/json" -Body $testEvent

kita cek statnya

Invoke-RestMethod -Uri http://localhost:8080/stats

kemudian kita coba hentikan servicenya

docker-compose down

kemudian kita coba testing

psytest tests/ -v