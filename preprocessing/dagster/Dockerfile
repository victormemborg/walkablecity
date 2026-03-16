FROM python:3.12-bookworm AS tippecanoe-builder

WORKDIR /build
RUN git clone https://github.com/felt/tippecanoe.git

WORKDIR /build/tippecanoe
RUN make -j
RUN make install


FROM python:3.12-bookworm AS dagster-runner

COPY --from=tippecanoe-builder /usr/local/bin/tippecanoe /usr/local/bin/

WORKDIR /opt/dagster/app

# Copy only requirements first for Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add code location code
COPY . .

# Run dagster code server on port 4000
EXPOSE 4000

# CMD allows this to be overridden from run launchers or executors to execute runs and steps
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-f", "definitions.py"]