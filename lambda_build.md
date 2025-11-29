# Guía para generar lambda_payload.zip usando Docker (Python 3.13)

## 1. Crear carpeta limpia lambda_build

```bash
rm -rf lambda_build
```
```bash
rm -rf lambda_deployment.zip
```
```bash
mkdir lambda_build
```

## 2. Copiar únicamente el código necesario

```bash
cp -r storeapi lambda_build/
cp -r utils lambda_build/
cp -r message_broker lambda_build/
cp requirements.txt lambda_build/
```

## 3. Instalar dependencias dentro del contenedor AWS Lambda Python 3.13 (x86_64)

```bash
docker run --platform linux/amd64 --rm \
  -v "$PWD/lambda_build":/var/task \
  --entrypoint /bin/bash \
  public.ecr.aws/lambda/python:3.13 \
  -c "pip install -r requirements.txt -t /var/task"
```

## 4. Crear el archivo ZIP final

```bash
cd lambda_build
zip -r ../lambda_deployment.zip .
cd ..
```

## 5. Subir el ZIP a AWS Lambda

Entrar a AWS Console → Lambda → tu función → Code → Upload from → .zip file → seleccionar lambda_deployment.zip.
```
https://anb-s3-storage.s3.us-east-2.amazonaws.com/lambda_deployment.zip
```

## 6. Payload para probar /health en AWS Lambda

```json
{
  "version": "2.0",
  "routeKey": "GET /health",
  "rawPath": "/health",
  "rawQueryString": "",
  "headers": { "host": "example.com" },
  "requestContext": {
    "http": {
      "method": "GET",
      "path": "/health",
      "protocol": "HTTP/1.1",
      "sourceIp": "1.2.3.4",
      "userAgent": "curl/7.64.1"
    }
  },
  "isBase64Encoded": false
}
```

```json
{
  "version": "2.0",
  "routeKey": "POST /api/auth/login",
  "rawPath": "/api/auth/login",
  "rawQueryString": "",
  "headers": {
    "content-type": "application/x-www-form-urlencoded"
  },
  "requestContext": {
    "http": {
      "method": "POST",
      "path": "/api/auth/login",
      "protocol": "HTTP/1.1",
      "sourceIp": "1.2.3.4",
      "userAgent": "curl"
    }
  },
  "body": "username=user@example.com&password=1234",
  "isBase64Encoded": false
}
```
