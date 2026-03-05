## How to run with tiling

1. Download latest build of pg_tileserv from https://github.com/CrunchyData/pg_tileserv/tree/master

2. Point DATABASE_URL to your PostGIS database and run pg_tileserv
```bash
    export DATABASE_URL='postgresql://username:password@host/dbname'
    ./pg_tileserv
```

3. In a seperate terminal: 
```bash
cd project/root/15-minute-cities
pnpm dev
```