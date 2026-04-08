# vehron
VEHRON — VEHicle, Research & Optimisation Network

## Development setup

```bash
source .venv/bin/activate
pip install -e .
```

## Run a BEV simulation

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/flat_highway_100kmh.yaml
```

## Run tests

```bash
pytest tests/unit tests/integration/test_bev_car_flat.py -q
```
