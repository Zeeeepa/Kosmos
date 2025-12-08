"""
Metabolomics Analysis for Biology Domain

Based on kosmos-figures Figure 2 pattern:
- Metabolite categorization by pathway (purine/pyrimidine/other)
- Classification by type (salvage precursor vs synthesis product)
- Statistical group comparisons with T-test/ANOVA
- Pathway-level pattern detection

Example workflow:
    analyzer = MetabolomicsAnalyzer()

    # Categorize a metabolite
    category = analyzer.categorize_metabolite('Adenosine')
    # Returns: {'category': 'purine', 'metabolite_type': 'salvage_precursor', ...}

    # Analyze group comparison
    results = analyzer.analyze_group_comparison(
        data_df=metabolomics_data,
        group1_samples=['Control_1', 'Control_2', 'Control_3'],
        group2_samples=['Treatment_1', 'Treatment_2', 'Treatment_3'],
        metabolites=['Adenosine', 'AMP', 'ATP', ...]
    )

    # Detect pathway patterns
    patterns = analyzer.analyze_pathway_pattern(results)
"""

from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats
from pydantic import BaseModel, Field, ConfigDict

from kosmos.domains.biology.apis import KEGGClient
from kosmos.utils.compat import model_to_dict


# Enums for metabolite classification
class MetaboliteCategory(str, Enum):
    """Biochemical pathway category"""
    PURINE = "purine"
    PYRIMIDINE = "pyrimidine"
    AMINO_ACID = "amino_acid"
    LIPID = "lipid"
    CARBOHYDRATE = "carbohydrate"
    OTHER = "other"


class MetaboliteType(str, Enum):
    """Type of metabolite in pathway"""
    SALVAGE_PRECURSOR = "salvage_precursor"
    SYNTHESIS_PRODUCT = "synthesis_product"
    INTERMEDIATE = "intermediate"
    DEGRADATION_PRODUCT = "degradation_product"
    UNKNOWN = "unknown"


# Pydantic models for results
class MetabolomicsResult(BaseModel):
    """Result from metabolite group comparison"""
    metabolite: str
    category: MetaboliteCategory
    metabolite_type: MetaboliteType
    group1_mean: float
    group2_mean: float
    log2_fold_change: float
    t_statistic: float
    p_value: float
    significant: bool = Field(default=False)
    pathways: List[str] = Field(default_factory=list)

    model_config = ConfigDict(use_enum_values=True)


class PathwayPattern(BaseModel):
    """Pathway-level pattern analysis result"""
    pathway_category: MetaboliteCategory
    metabolite_type: MetaboliteType
    n_metabolites: int
    mean_log2_fc: float
    median_log2_fc: float
    n_increased: int
    n_decreased: int
    n_significant: int
    pattern_description: str
    pattern_p_value: Optional[float] = None

    model_config = ConfigDict(use_enum_values=True)


class PathwayComparison(BaseModel):
    """Comparison between pathway groups (e.g., salvage vs synthesis)"""
    category: MetaboliteCategory
    salvage_mean_fc: float
    synthesis_mean_fc: float
    difference: float
    t_statistic: float
    p_value: float
    pattern: str  # e.g., "salvage_decreased_synthesis_increased"
    significant: bool

    model_config = ConfigDict(use_enum_values=True)


class MetabolomicsAnalyzer:
    """
    Analyzer for metabolomics data following Figure 2 pattern.

    Provides:
    - Metabolite categorization by pathway and type
    - Statistical group comparisons
    - Pathway-level pattern detection
    - Integration with KEGG for pathway information
    """

    # Purine nucleotides and derivatives
    PURINE_METABOLITES = [
        'Adenine', 'Adenosine', 'AMP', 'ADP', 'ATP',
        'Guanine', 'Guanosine', 'GMP', 'GDP', 'GTP',
        'Inosine', 'IMP', 'Hypoxanthine', 'Xanthine',
        'Xanthosine', 'XMP', 'dAMP', 'dADP', 'dATP',
        'dGMP', 'dGDP', 'dGTP', 'cAMP', 'cGMP'
    ]

    # Pyrimidine nucleotides and derivatives
    PYRIMIDINE_METABOLITES = [
        'Cytosine', 'Cytidine', 'CMP', 'CDP', 'CTP',
        'Uracil', 'Uridine', 'UMP', 'UDP', 'UTP',
        'Thymine', 'Thymidine', 'TMP', 'TDP', 'TTP',
        'dCMP', 'dCDP', 'dCTP', 'dUMP', 'dUDP', 'dUTP',
        'Orotate', 'Dihydroorotate'
    ]

    # Salvage pathway precursors (bases and nucleosides)
    SALVAGE_PRECURSORS = [
        'Adenine', 'Adenosine', 'Guanine', 'Guanosine',
        'Hypoxanthine', 'Inosine', 'Xanthine', 'Xanthosine',
        'Cytosine', 'Cytidine', 'Uracil', 'Uridine',
        'Thymine', 'Thymidine'
    ]

    # De novo synthesis products (nucleotides)
    SYNTHESIS_PRODUCTS = [
        'AMP', 'GMP', 'IMP', 'XMP',
        'CMP', 'UMP', 'TMP',
        'dAMP', 'dGMP', 'dCMP', 'dUMP', 'dTMP'
    ]

    def __init__(self, kegg_client: Optional[KEGGClient] = None):
        """
        Initialize MetabolomicsAnalyzer.

        Args:
            kegg_client: Optional KEGGClient instance for pathway queries.
                        If None, creates a new instance.
        """
        self.kegg_client = kegg_client or KEGGClient()

    def categorize_metabolite(
        self,
        compound_name: str,
        use_kegg: bool = True
    ) -> Dict[str, Any]:
        """
        Categorize a metabolite by pathway and type.

        Args:
            compound_name: Name of the metabolite
            use_kegg: Whether to query KEGG for pathway information

        Returns:
            Dictionary with category, metabolite_type, and pathways
        """
        # Normalize compound name
        compound_clean = compound_name.strip()

        # Determine category
        category = self._determine_category(compound_clean, use_kegg)

        # Determine metabolite type
        metabolite_type = self._determine_type(compound_clean)

        # Get pathway information from KEGG if requested
        pathways = []
        if use_kegg:
            try:
                kegg_info = self.kegg_client.categorize_metabolite(compound_clean)
                if kegg_info and 'pathways' in kegg_info:
                    pathways = kegg_info['pathways']
            except Exception as e:
                # Silently fail KEGG queries, use heuristics only
                pass

        return {
            'compound_name': compound_clean,
            'category': category,
            'metabolite_type': metabolite_type,
            'pathways': pathways
        }

    def _determine_category(
        self,
        compound_name: str,
        use_kegg: bool = True
    ) -> MetaboliteCategory:
        """Determine metabolite pathway category"""
        # Check against known lists first (fast)
        if compound_name in self.PURINE_METABOLITES:
            return MetaboliteCategory.PURINE
        elif compound_name in self.PYRIMIDINE_METABOLITES:
            return MetaboliteCategory.PYRIMIDINE

        # Check by name patterns
        compound_lower = compound_name.lower()

        # Purine patterns
        if any(pattern in compound_lower for pattern in [
            'adenine', 'adenosine', 'guanine', 'guanosine',
            'inosine', 'hypoxanthine', 'xanthine'
        ]):
            return MetaboliteCategory.PURINE

        # Pyrimidine patterns
        if any(pattern in compound_lower for pattern in [
            'cytosine', 'cytidine', 'uracil', 'uridine',
            'thymine', 'thymidine', 'orotate'
        ]):
            return MetaboliteCategory.PYRIMIDINE

        # Amino acid patterns
        if any(pattern in compound_lower for pattern in [
            'alanine', 'glycine', 'leucine', 'isoleucine',
            'valine', 'lysine', 'arginine', 'glutamate',
            'aspartate', 'serine', 'threonine'
        ]):
            return MetaboliteCategory.AMINO_ACID

        # Lipid patterns
        if any(pattern in compound_lower for pattern in [
            'fatty acid', 'phospholipid', 'sphingolipid',
            'cholesterol', 'triglyceride'
        ]):
            return MetaboliteCategory.LIPID

        # Carbohydrate patterns
        if any(pattern in compound_lower for pattern in [
            'glucose', 'fructose', 'galactose', 'mannose',
            'ribose', 'glycogen', 'sucrose'
        ]):
            return MetaboliteCategory.CARBOHYDRATE

        return MetaboliteCategory.OTHER

    def _determine_type(self, compound_name: str) -> MetaboliteType:
        """Determine metabolite type (salvage vs synthesis)"""
        # Check against known lists
        if compound_name in self.SALVAGE_PRECURSORS:
            return MetaboliteType.SALVAGE_PRECURSOR
        elif compound_name in self.SYNTHESIS_PRODUCTS:
            return MetaboliteType.SYNTHESIS_PRODUCT

        # Pattern-based classification
        compound_lower = compound_name.lower()

        # Salvage precursors: bases and nucleosides (end in -ine or -osine)
        if compound_name.endswith(('ine', 'osine')) and not any(
            x in compound_lower for x in ['mp', 'dp', 'tp']
        ):
            return MetaboliteType.SALVAGE_PRECURSOR

        # Synthesis products: nucleotides (contain MP, DP, TP)
        if any(x in compound_name for x in ['MP', 'DP', 'TP']):
            # But exclude salvage-like names
            if not compound_name.endswith(('ine', 'osine')):
                return MetaboliteType.SYNTHESIS_PRODUCT

        # Degradation products
        if any(pattern in compound_lower for pattern in [
            'uric acid', 'allantoin', 'urea', 'beta-alanine'
        ]):
            return MetaboliteType.DEGRADATION_PRODUCT

        return MetaboliteType.INTERMEDIATE

    def analyze_group_comparison(
        self,
        data_df: pd.DataFrame,
        group1_samples: List[str],
        group2_samples: List[str],
        metabolites: Optional[List[str]] = None,
        log2_transform: bool = True,
        p_threshold: float = 0.05,
        use_kegg: bool = False  # Disabled by default for speed
    ) -> List[MetabolomicsResult]:
        """
        Perform statistical comparison between two groups.

        Args:
            data_df: DataFrame with metabolites as rows, samples as columns
            group1_samples: Sample names for group 1
            group2_samples: Sample names for group 2
            metabolites: List of metabolites to analyze (None = all)
            log2_transform: Whether to apply log2 transformation
            p_threshold: P-value threshold for significance
            use_kegg: Whether to query KEGG for pathway info (slow)

        Returns:
            List of MetabolomicsResult objects
        """
        # Select metabolites
        if metabolites is None:
            metabolites = data_df.index.tolist()

        # Verify samples exist
        missing_group1 = [s for s in group1_samples if s not in data_df.columns]
        missing_group2 = [s for s in group2_samples if s not in data_df.columns]
        if missing_group1 or missing_group2:
            raise ValueError(
                f"Missing samples - Group1: {missing_group1}, Group2: {missing_group2}"
            )

        # Apply log2 transformation if requested
        if log2_transform:
            # Add pseudocount to avoid log(0)
            df_transformed = np.log2(data_df + 1)
        else:
            df_transformed = data_df.copy()

        results = []

        for metabolite in metabolites:
            if metabolite not in df_transformed.index:
                continue

            # Get values for each group
            group1_values = df_transformed.loc[metabolite, group1_samples].values
            group2_values = df_transformed.loc[metabolite, group2_samples].values

            # Skip if all NaN
            if np.all(np.isnan(group1_values)) or np.all(np.isnan(group2_values)):
                continue

            # Remove NaN values
            group1_clean = group1_values[~np.isnan(group1_values)]
            group2_clean = group2_values[~np.isnan(group2_values)]

            # Calculate statistics
            group1_mean = np.mean(group1_clean)
            group2_mean = np.mean(group2_clean)
            log2_fc = group1_mean - group2_mean

            # T-test
            try:
                t_stat, p_val = stats.ttest_ind(group1_clean, group2_clean)
            except Exception:
                # Handle edge cases (e.g., zero variance)
                t_stat, p_val = 0.0, 1.0

            # Categorize metabolite
            categorization = self.categorize_metabolite(metabolite, use_kegg=use_kegg)

            # Create result
            result = MetabolomicsResult(
                metabolite=metabolite,
                category=categorization['category'],
                metabolite_type=categorization['metabolite_type'],
                group1_mean=float(group1_mean),
                group2_mean=float(group2_mean),
                log2_fold_change=float(log2_fc),
                t_statistic=float(t_stat),
                p_value=float(p_val),
                significant=(p_val < p_threshold),
                pathways=categorization['pathways']
            )

            results.append(result)

        return results

    def analyze_pathway_pattern(
        self,
        results: List[MetabolomicsResult],
        category_filter: Optional[MetaboliteCategory] = None
    ) -> List[PathwayPattern]:
        """
        Analyze pathway-level patterns from metabolomics results.

        Args:
            results: List of MetabolomicsResult objects
            category_filter: Optional filter for specific category

        Returns:
            List of PathwayPattern objects summarizing pathway trends
        """
        if not results:
            return []

        # Convert to DataFrame for easier grouping
        results_df = pd.DataFrame([model_to_dict(r) for r in results])

        # Filter by category if specified
        if category_filter:
            results_df = results_df[results_df['category'] == category_filter.value]

        patterns = []

        # Group by category and metabolite_type
        for (category, met_type), group in results_df.groupby(['category', 'metabolite_type']):
            n_metabolites = len(group)
            mean_fc = group['log2_fold_change'].mean()
            median_fc = group['log2_fold_change'].median()
            n_increased = (group['log2_fold_change'] > 0).sum()
            n_decreased = (group['log2_fold_change'] < 0).sum()
            n_significant = group['significant'].sum()

            # Describe pattern
            if mean_fc > 0.5:
                direction = "increased"
            elif mean_fc < -0.5:
                direction = "decreased"
            else:
                direction = "unchanged"

            pattern_desc = f"{category} {met_type} metabolites are {direction}"
            if n_significant > 0:
                pattern_desc += f" ({n_significant}/{n_metabolites} significant)"

            pattern = PathwayPattern(
                pathway_category=MetaboliteCategory(category),
                metabolite_type=MetaboliteType(met_type),
                n_metabolites=int(n_metabolites),
                mean_log2_fc=float(mean_fc),
                median_log2_fc=float(median_fc),
                n_increased=int(n_increased),
                n_decreased=int(n_decreased),
                n_significant=int(n_significant),
                pattern_description=pattern_desc
            )

            patterns.append(pattern)

        return patterns

    def compare_salvage_vs_synthesis(
        self,
        results: List[MetabolomicsResult],
        category: MetaboliteCategory = MetaboliteCategory.PURINE
    ) -> Optional[PathwayComparison]:
        """
        Compare salvage vs synthesis pathways (Figure 2 pattern).

        This is the key analysis from Figure 2: detecting whether salvage
        precursors decrease while synthesis products increase (or vice versa).

        Args:
            results: List of MetabolomicsResult objects
            category: Which pathway category to analyze (default: purine)

        Returns:
            PathwayComparison object or None if insufficient data
        """
        # Filter results by category
        category_results = [r for r in results if r.category == category]
        if not category_results:
            return None

        # Separate salvage and synthesis
        salvage = [
            r for r in category_results
            if r.metabolite_type == MetaboliteType.SALVAGE_PRECURSOR
        ]
        synthesis = [
            r for r in category_results
            if r.metabolite_type == MetaboliteType.SYNTHESIS_PRODUCT
        ]

        if not salvage or not synthesis:
            return None

        # Calculate mean fold changes
        salvage_fcs = [r.log2_fold_change for r in salvage]
        synthesis_fcs = [r.log2_fold_change for r in synthesis]

        salvage_mean = np.mean(salvage_fcs)
        synthesis_mean = np.mean(synthesis_fcs)
        difference = synthesis_mean - salvage_mean

        # Test if significantly different
        try:
            t_stat, p_val = stats.ttest_ind(salvage_fcs, synthesis_fcs)
        except Exception:
            t_stat, p_val = 0.0, 1.0

        # Determine pattern
        if salvage_mean < -0.5 and synthesis_mean > 0.5:
            pattern = "salvage_decreased_synthesis_increased"
        elif salvage_mean > 0.5 and synthesis_mean < -0.5:
            pattern = "salvage_increased_synthesis_decreased"
        elif abs(salvage_mean - synthesis_mean) < 0.3:
            pattern = "no_differential_pattern"
        else:
            pattern = "mixed_pattern"

        return PathwayComparison(
            category=category,
            salvage_mean_fc=float(salvage_mean),
            synthesis_mean_fc=float(synthesis_mean),
            difference=float(difference),
            t_statistic=float(t_stat),
            p_value=float(p_val),
            pattern=pattern,
            significant=(p_val < 0.05)
        )
