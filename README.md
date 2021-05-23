# Iroha metrics reader

This repository for interaction with Iroha and get metrics through Prometheus endpoint.

## Run
```bash
make
...
locust -f ./reader/metrics_reader.py -u 1 -r 1 --headless
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.