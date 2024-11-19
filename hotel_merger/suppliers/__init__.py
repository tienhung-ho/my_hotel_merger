from .acme import AcmeSupplier
from .patagonia import PatagoniaSupplier
from .paperflies import PaperfliesSupplier

SUPPLIERS = {
    "acme": AcmeSupplier,
    "patagonia": PatagoniaSupplier,
    "paperflies": PaperfliesSupplier,
}
