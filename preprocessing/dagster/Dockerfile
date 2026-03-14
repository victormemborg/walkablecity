FROM python:3.12-bookworm

WORKDIR /opt/dagster/app

# Copy only requirements first for Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add code location code
COPY . .

# Run dagster code server on port 4000
EXPOSE 4000

HEALTHCHECK --timeout=1s --start-period=3s --interval=3s --retries=20 CMD ["dagster", "api", "grpc-health-check", "-p", "4000"]

# CMD allows this to be overridden from run launchers or executors to execute runs and steps
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-f", "definitions.py"]