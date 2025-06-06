# Contrato PF View
# This file is a wrapper around the modular implementation in views/contrato_pf/
from views.contrato_pf.main_view import ContratoPFView

# For backward compatibility
__all__ = ['ContratoPFView', 'ContratoPFForm']

# Import ContratoPFForm for backward compatibility
from views.contrato_pf.contract_form import ContratoPFForm
