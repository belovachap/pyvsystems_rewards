# pyvsystems_rewards

This library provides the accounting required to operate a successful and
transparent v.systems supernode.

## Quick Start

The library is still in "alpha" but is being used to generate the automated
reporting for [Peercoin's VPool](https://forum.v.systems/t/introducing-peercoin-vpool-to-the-vsys-community/173)
at http://vsys.peercoin-library.org/.

You can use the library by pip installing it from [PyPi](https://pypi.org/project/pyvsystems-rewards/):

```
pip install pyvsystems-rewards
```

## Development

To work on the library:

1. `git clone https://github.com/belovachap/pyvsystems_rewards.git`
2. `cd pyvsystems_rewards`
3. `virtualenv -p python3 venv`
4. `source venv/bin/activate`
6. `pip install -r requirements-dev.txt`

Unit tests can be run with `pytest test`.

## Releasing On PyPi

1. Update the version number in `setup.py`
2. `make clean`
3. `make`
4. `make upload`

## Use Cases

Other initiatives using this library:

* [pyvsystems-distributions](https://github.com/belovachap/pyvsystems_distributions)
* [pyvsystems-reports](https://github.com/belovachap/pyvsystems_reports)

## Future Work

* Write unit tests that consume real world data and produce vetted results.
* Release a 0.1.0 version.
