ARG PYTHON_BASE=python:3.11.13-alpine3.22@sha256:6849ab1bde2e04f50c866a51c7f794b4388d1c7dcaee84470c4d67544dec8806

FROM ${PYTHON_BASE} AS builder
WORKDIR /build
COPY pyproject.toml ./
COPY afims_r ./afims_r
COPY requirements.lock ./
RUN python -m pip install --disable-pip-version-check --no-cache-dir --upgrade pip==24.0 setuptools==80.9.0 wheel==0.46.3     && python -m pip wheel --no-cache-dir --wheel-dir /wheelhouse -r requirements.lock     && python -m pip wheel --no-cache-dir --no-deps --wheel-dir /wheelhouse .

FROM ${PYTHON_BASE} AS runtime
LABEL org.opencontainers.image.source="https://github.com/zablotnydawid-tdk/-AFIMS-R"
RUN apk upgrade --no-cache libcrypto3 libssl3 musl musl-utils zlib
WORKDIR /app
COPY --from=builder /wheelhouse /wheelhouse
COPY requirements.lock /tmp/requirements.lock
RUN python -m pip install --disable-pip-version-check --no-cache-dir --no-index --find-links=/wheelhouse -r /tmp/requirements.lock afims-r==0.4.0     && python -m pip uninstall -y pip setuptools wheel     && rm -rf /wheelhouse /root/.cache /tmp/requirements.lock
RUN addgroup -S afims && adduser -S -G afims afims
USER afims
EXPOSE 8000
CMD ["uvicorn", "afims_r.api:app", "--host", "0.0.0.0", "--port", "8000"]
