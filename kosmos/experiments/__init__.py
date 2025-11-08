"""
Experiment execution and design system.

Provides templates, resource estimation, and validation for experiments.
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
