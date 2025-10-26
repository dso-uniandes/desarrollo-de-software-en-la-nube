## Escenario 1 - Sanidad (Smoke):

Se ajustan los hilos y el ramp-up period

<img width="1519" height="856" alt="java_GLTQw7kwge" src="https://github.com/user-attachments/assets/5bdb580a-83ad-4bff-a666-e49b65cb069e" />

Configuración de la petición:

<img width="1519" height="856" alt="java_TE3ziuAjav" src="https://github.com/user-attachments/assets/531da995-64b9-4b56-9687-71351d85add3" />

Results tree

<img width="1519" height="856" alt="java_0WpDjov8j2" src="https://github.com/user-attachments/assets/a07d8133-4dda-468f-ac19-894ed22fa159" />

Summary report

<img width="1519" height="856" alt="java_5JfaZ5r1M8" src="https://github.com/user-attachments/assets/496397c9-1ce6-4001-9cb2-19bc680547a9" />

Aggregate report

<img width="1519" height="856" alt="java_ErSibnIBm4" src="https://github.com/user-attachments/assets/4772e192-21bb-4c70-9dc4-ec4e69321ff2" />

Response-time graph

<img width="1519" height="856" alt="java_rOpBp4TdaX" src="https://github.com/user-attachments/assets/b84f74d7-9766-4619-9f1c-872515e23a18" />

Graph results

<img width="1519" height="856" alt="java_XCSEdQx20G" src="https://github.com/user-attachments/assets/c4f3d6ff-efef-406c-b2fd-abc2f86fe3bf" />

Con calculate-stats en el EC2 se generó el gráfico de...

<img width="1920" height="1726" alt="image" src="https://github.com/user-attachments/assets/ae472958-d251-49f7-975b-91d50c363e94" />

Luego se descargó la imagen generada con secure copy:

scp -i "ANB.pem" ubuntu@{{ip}}:/home/ubuntu/anb/capacity-planning/postman/results/container_resources.png ./container_resources.png

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/31f3c92d-6b42-4e65-8c28-31a0e16f7016" />

## Escenario 1 - Escalamiento rápido (Ramp) X = 100 :

Summary report

<img width="1467" height="801" alt="java_TOYLZpBFWs" src="https://github.com/user-attachments/assets/06d49d2c-028d-402f-9480-cfaaae7c9221" />

Aggregate report

<img width="1467" height="801" alt="java_1YL9a5qtSc" src="https://github.com/user-attachments/assets/5ef849cf-24b1-4dee-920f-5ba0d2d6c929" />

Response-time graph

<img width="1467" height="801" alt="java_CMYt9fWng5" src="https://github.com/user-attachments/assets/5d060f5b-fecb-4709-a340-61347725fe8b" />

Graph results

<img width="1467" height="801" alt="java_T1g88d5sYG" src="https://github.com/user-attachments/assets/c67dad2d-f371-4dd0-bb7f-4af67e33e7ff" />

calculate-stats:

<img width="1920" height="1704" alt="image" src="https://github.com/user-attachments/assets/a9b82748-d342-495c-a728-3e6e2b56a0c2" />

Gráfico:

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/48ee57d7-02b2-45e2-b8d0-e231e0ade0fe" />

## Escenario 1 - Escalamiento rápido (Ramp) X = 300 :

Summary report

<img width="1467" height="801" alt="java_8XfTceekM3" src="https://github.com/user-attachments/assets/e1c88317-c01b-4df6-89ae-77fd2d57fd2f" />

Aggregate report

<img width="1467" height="801" alt="java_Yt914qjvWT" src="https://github.com/user-attachments/assets/37257a2f-ce58-4dfd-bb00-235ddf5c93bf" />

Response-time graph

<img width="1467" height="801" alt="java_QbncFsrJQo" src="https://github.com/user-attachments/assets/7f5ba010-41d9-4529-9ec7-880b0b37c13b" />

Graph results

<img width="1467" height="801" alt="java_0bwM9nL3gJ" src="https://github.com/user-attachments/assets/00859e86-703a-47bf-b8d3-3003c0e4dc2a" />

calculate-stats:

<img width="1920" height="1704" alt="image" src="https://github.com/user-attachments/assets/cbeb5e60-b284-4a0c-8799-7eb52d4ed8c6" />

Gráfico:

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/9c36a0a9-1dfe-4bba-a9f3-832d85bcddb9" />

## Escenario 1 - Escalamiento rápido (Ramp) X = 500 :

Summary report

<img width="1467" height="801" alt="java_SeVT6L9y5S" src="https://github.com/user-attachments/assets/fc7f0d46-5ae7-4786-a252-f2244c65366e" />

Aggregate report

<img width="1467" height="801" alt="java_xvUmw0GM0T" src="https://github.com/user-attachments/assets/d168cbe3-fbe5-44ae-ad81-e21dabd35a65" />

Response-time graph

<img width="1467" height="801" alt="java_sEj6Om40Nr" src="https://github.com/user-attachments/assets/07cade6e-ddf0-47b1-9966-19c18896f793" />

Graph results

<img width="1754" height="801" alt="java_boAxAlMMBP" src="https://github.com/user-attachments/assets/0faf9013-5d34-419f-b883-3b5cf3b9dc53" />

calculate-stats:

<img width="903" height="216" alt="image" src="https://github.com/user-attachments/assets/28edeb81-f280-4ed0-b5b3-913ef76f2142" />

Gráfico:

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/656dd095-32cb-4180-9077-f6a126e1b7f2" />

## Escenario 1 - Sostenida corta (300 * 0.8 = 240) :

Summary report

<img width="1480" height="814" alt="java_quhkRDFM0y" src="https://github.com/user-attachments/assets/74ced228-becc-4f3e-896d-93298a615818" />

Aggregate report

<img width="1480" height="814" alt="java_ZMvmCPWbfW" src="https://github.com/user-attachments/assets/2ea1fd22-6882-41c1-a25b-f137e453267e" />

Response-time graph

<img width="1226" height="814" alt="java_4ohOTcarIn" src="https://github.com/user-attachments/assets/857a06b3-847d-43bf-ab69-5031af3fdc7c" />

Graph results

<img width="1226" height="814" alt="java_VWpGT4aaBJ" src="https://github.com/user-attachments/assets/d16b3857-b43e-475d-bafc-370fa3b9ea9f" />

calculate-stats:

<img width="1536" height="1257" alt="image" src="https://github.com/user-attachments/assets/89452f9c-e917-4850-ad1e-3b7104af75ed" />

Gráfico:

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/1ca56b6c-6d84-4b00-b2ca-2f74fe4f6f27" />












