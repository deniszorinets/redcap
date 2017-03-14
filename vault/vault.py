# vault
import hvac


class KeyManager:
    """
        interface for secret storing backend
    """

    def get(self, *args, **kwargs) -> dict:
        """
        get secret
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    def set(self, *args, **kwargs) -> dict:
        """
        save secret
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    def delete(self, *args, **kwarg) -> dict:
        """
        delete secret
        :param args:
        :param kwarg:
        :return:
        """
        raise NotImplementedError()


class VaultKeyManager(KeyManager):
    """
    vault secret secret storing backend
    """
    def __init__(self, vault: hvac.Client) -> None:
        self.vault = vault

    def get(self, *args, **kwargs) -> dict:
        """
        get secret
        :param args:
        :param kwargs:
        :return:
        """
        return self.vault.read(*args, **kwargs)

    def set(self, *args, **kwargs) -> dict:
        """
        save secret
        :param args:
        :param kwargs:
        :return:
        """
        return self.vault.write(*args, **kwargs)

    def delete(self, *args, **kwargs) -> dict:
        """
        delete secret
        :param args:
        :param kwargs:
        :return:
        """
        return self.vault.delete(*args, **kwargs)
