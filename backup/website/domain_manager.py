from inspect import isabstract, isclass

from . import domain        

_available_domains = [attr for attr in domain.__dict__.values() if isclass(
    attr) and not isabstract(attr) and issubclass(attr, domain.Site)]

domain_map = {domain_.domain: domain_ for domain_ in _available_domains}
