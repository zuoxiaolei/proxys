import pytest
import proxys


def test_get_random_proxy():
    random_proxy = proxys.get_random_proxy()
    assert random_proxy
    assert ":" in random_proxy


def test_get_all_proxy():
    all_proxy = proxys.get_all_proxy()
    assert len(all_proxy) > 5


def test_validate_proxy():
    all_proxy = proxys.get_all_proxy()
    validated_all_proxy = proxys.validate_proxy_pool(all_proxy[:10])
    assert len(validated_all_proxy) > 0


if __name__ == '__main__':
    pytest.main()
