import redcap.settings as settings

# vault
import hvac

vault = hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)
