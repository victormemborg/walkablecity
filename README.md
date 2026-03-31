# Bachelor-Thesis

## Running the project locally

Assuming you have preprocessed the tiles, place the processed tiles in the `tiles/` directory (should probably be mounted as a volume in the future, but for now we just have it here). Then, run the following command to start the project:

```bash
docker compose -f docker-compose.benchmark.yml up martin nginx
```

> [!NOTE]
> You can also run the entire stack with `docker compose -f docker-compose.benchmark.yml up`, but be aware that the frontend will not reflect changes immediately, as it is built into the image. If you want to see changes to the frontend immediately, you can run it separately with `npm run dev` as described below.

Now you have a reverse proxy running on `http://localhost:8080` that forwards requests to the tile server (port 3001) and the web application (port 3000). You can access the web application at `http://localhost:8080` and the tile server at `http://localhost:8080/tiles`. Remember to start the frontend as well, which is not included in the docker compose file for now.

```bash
cd 15-minute-cities
npm install
npm run dev
```

I recommend accessing the frontend on port 3000 as changes to the frontend will be reflected immediately, unlike the port 8080.
