"""
Experiment protocol templates.

Provides template system for generating experiment protocols.
"""

from kosmos.experiments.templates.base import (
    TemplateBase,
    TemplateRegistry,
    TemplateMetadata,
    TemplateCustomizationParams,
    TemplateValidationResult,
    get_template_registry,
    register_template,
)

__all__ = [
    "TemplateBase",
    "TemplateRegistry",
    "TemplateMetadata",
    "TemplateCustomizationParams",
    "TemplateValidationResult",
    "get_template_registry",
    "register_template",
]
