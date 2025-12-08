"""
Genomics Analysis for Biology Domain

Based on kosmos-figures Figure 5 pattern:
- GWAS multi-modal data integration
- Composite scoring framework (0-55 points)
- eQTL/pQTL concordance validation
- SNP-gene mechanism ranking

Example workflow:
    analyzer = GenomicsAnalyzer()

    # Multi-modal integration for SNP-gene pair
    result = analyzer.multi_modal_integration(
        snp_id='rs7903146',
        gene='TCF7L2',
        gwas_data=gwas_df,
        eqtl_data=eqtl_df,
        pqtl_data=pqtl_df,
        atac_data=atac_df
    )

    # Batch analysis for multiple SNPs
    results = analyzer.analyze_snp_list(
        snp_ids=['rs7903146', 'rs12255372', ...],
        gene='TCF7L2'
    )

    # Rank mechanisms by composite score
    top_mechanisms = analyzer.rank_mechanisms(results, top_n=10)
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats
from pydantic import BaseModel, Field, ConfigDict

from kosmos.domains.biology.apis import (
    GWASCatalogClient,
    GTExClient,
    ENCODEClient,
    dbSNPClient,
    EnsemblClient
)


# Enums for genomic evidence
class EvidenceLevel(str, Enum):
    """Level of evidence for genetic variant"""
    VERY_HIGH = "very_high"  # >40 points
    HIGH = "high"  # 30-40 points
    MODERATE = "moderate"  # 20-30 points
    LOW = "low"  # 10-20 points
    VERY_LOW = "very_low"  # <10 points


class EffectDirection(str, Enum):
    """Direction of genetic effect"""
    PROTECTIVE = "protective"
    RISK = "risk"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


# Pydantic models for genomics results
class CompositeScore(BaseModel):
    """Composite score breakdown (max 55 points from Figure 5)"""
    gwas_score: float = Field(ge=0, le=10, description="GWAS evidence (0-10)")
    qtl_score: float = Field(ge=0, le=15, description="QTL evidence (0-15)")
    tf_score: float = Field(ge=0, le=10, description="TF disruption (0-10)")
    expression_score: float = Field(ge=0, le=5, description="Expression change (0-5)")
    protective_score: float = Field(ge=0, le=15, description="Protective evidence (0-15)")
    total_score: float = Field(ge=0, le=55, description="Total composite score")

    def get_evidence_level(self) -> EvidenceLevel:
        """Determine evidence level from total score"""
        if self.total_score >= 40:
            return EvidenceLevel.VERY_HIGH
        elif self.total_score >= 30:
            return EvidenceLevel.HIGH
        elif self.total_score >= 20:
            return EvidenceLevel.MODERATE
        elif self.total_score >= 10:
            return EvidenceLevel.LOW
        else:
            return EvidenceLevel.VERY_LOW


class GenomicsResult(BaseModel):
    """Result from genomic multi-modal integration"""
    snp_id: str
    gene: str
    chromosome: Optional[str] = None
    position: Optional[int] = None

    # GWAS data
    gwas_p_value: Optional[float] = None
    gwas_beta: Optional[float] = None
    gwas_trait: Optional[str] = None
    gwas_posterior_prob: Optional[float] = None

    # eQTL data
    has_eqtl: bool = False
    eqtl_beta: Optional[float] = None
    eqtl_p_value: Optional[float] = None
    eqtl_tissue: Optional[str] = None

    # pQTL data
    has_pqtl: bool = False
    pqtl_beta: Optional[float] = None
    pqtl_p_value: Optional[float] = None

    # ATAC-seq data
    has_atac_peak: bool = False
    atac_significance: Optional[float] = None

    # TF binding
    n_disrupted_tfs: int = 0
    disrupted_tfs: List[str] = Field(default_factory=list)

    # Analysis results
    composite_score: CompositeScore
    evidence_level: EvidenceLevel
    effect_direction: EffectDirection
    concordant: bool = Field(
        default=False,
        description="Whether eQTL/pQTL effects agree with GWAS direction"
    )

    model_config = ConfigDict(use_enum_values=True)


class MechanismRanking(BaseModel):
    """Ranked list of SNP-gene mechanisms"""
    snp_id: str
    gene: str
    total_score: float
    evidence_level: EvidenceLevel
    effect_direction: EffectDirection
    key_evidence: List[str] = Field(
        default_factory=list,
        description="List of key supporting evidence"
    )
    rank: int

    model_config = ConfigDict(use_enum_values=True)


class GenomicsAnalyzer:
    """
    Analyzer for genomics data following Figure 5 pattern.

    Provides:
    - GWAS + eQTL + pQTL + ATAC multi-modal integration
    - Composite scoring framework (0-55 points)
    - Effect concordance validation
    - Mechanism ranking by evidence strength
    """

    def __init__(
        self,
        gwas_client: Optional[GWASCatalogClient] = None,
        gtex_client: Optional[GTExClient] = None,
        encode_client: Optional[ENCODEClient] = None,
        dbsnp_client: Optional[dbSNPClient] = None,
        ensembl_client: Optional[EnsemblClient] = None
    ):
        """
        Initialize GenomicsAnalyzer with API clients.

        Args:
            gwas_client: GWAS Catalog API client
            gtex_client: GTEx Portal API client
            encode_client: ENCODE API client
            dbsnp_client: dbSNP API client
            ensembl_client: Ensembl API client
        """
        self.gwas_client = gwas_client or GWASCatalogClient()
        self.gtex_client = gtex_client or GTExClient()
        self.encode_client = encode_client or ENCODEClient()
        self.dbsnp_client = dbsnp_client or dbSNPClient()
        self.ensembl_client = ensembl_client or EnsemblClient()

    def multi_modal_integration(
        self,
        snp_id: str,
        gene: str,
        gwas_data: Optional[Dict[str, Any]] = None,
        eqtl_data: Optional[Dict[str, Any]] = None,
        pqtl_data: Optional[Dict[str, Any]] = None,
        atac_data: Optional[Dict[str, Any]] = None,
        tf_data: Optional[List[str]] = None,
        fetch_missing: bool = True
    ) -> GenomicsResult:
        """
        Integrate multiple genomic data modalities for a SNP-gene pair.

        Args:
            snp_id: SNP identifier (e.g., 'rs7903146')
            gene: Gene symbol (e.g., 'TCF7L2')
            gwas_data: Pre-loaded GWAS data (optional)
            eqtl_data: Pre-loaded eQTL data (optional)
            pqtl_data: Pre-loaded pQTL data (optional)
            atac_data: Pre-loaded ATAC-seq data (optional)
            tf_data: Pre-loaded TF disruption data (optional)
            fetch_missing: Whether to fetch missing data from APIs

        Returns:
            GenomicsResult with integrated data and composite score
        """
        # Fetch missing data from APIs if requested
        if fetch_missing:
            if gwas_data is None:
                try:
                    gwas_data = self.gwas_client.get_variant(snp_id)
                except Exception:
                    gwas_data = None

            if eqtl_data is None:
                try:
                    eqtl_data = self.gtex_client.get_eqtl(snp_id, gene)
                except Exception:
                    eqtl_data = None

            if pqtl_data is None:
                try:
                    pqtl_data = self.gtex_client.get_pqtl(snp_id, gene)
                except Exception:
                    pqtl_data = None

            if atac_data is None:
                try:
                    atac_data = self.encode_client.get_atac_peaks(snp_id)
                except Exception:
                    atac_data = None

        # Extract data from responses
        chromosome = None
        position = None
        gwas_p = None
        gwas_beta = None
        gwas_trait = None
        gwas_posterior = None

        if gwas_data:
            chromosome = gwas_data.get('chromosome')
            position = gwas_data.get('position')
            gwas_p = gwas_data.get('p_value')
            gwas_beta = gwas_data.get('beta')
            gwas_trait = gwas_data.get('trait')
            gwas_posterior = gwas_data.get('posterior_probability')

        # eQTL data
        has_eqtl = eqtl_data is not None
        eqtl_beta = eqtl_data.get('beta') if eqtl_data else None
        eqtl_p = eqtl_data.get('p_value') if eqtl_data else None
        eqtl_tissue = eqtl_data.get('tissue') if eqtl_data else None

        # pQTL data
        has_pqtl = pqtl_data is not None
        pqtl_beta = pqtl_data.get('beta') if pqtl_data else None
        pqtl_p = pqtl_data.get('p_value') if pqtl_data else None

        # ATAC-seq data
        has_atac = atac_data is not None and atac_data.get('has_peak', False)
        atac_sig = atac_data.get('significance') if atac_data else None

        # TF disruption data
        disrupted_tfs = tf_data or []
        n_tfs = len(disrupted_tfs)

        # Calculate composite score
        composite = self.calculate_composite_score(
            gwas_p=gwas_p,
            gwas_beta=gwas_beta,
            gwas_posterior=gwas_posterior,
            has_eqtl=has_eqtl,
            eqtl_beta=eqtl_beta,
            has_pqtl=has_pqtl,
            pqtl_beta=pqtl_beta,
            has_atac=has_atac,
            n_disrupted_tfs=n_tfs
        )

        # Determine effect direction
        effect_dir = self._determine_effect_direction(gwas_beta)

        # Check concordance
        concordant = self.check_concordance(
            gwas_beta=gwas_beta,
            eqtl_beta=eqtl_beta,
            pqtl_beta=pqtl_beta
        )

        return GenomicsResult(
            snp_id=snp_id,
            gene=gene,
            chromosome=chromosome,
            position=position,
            gwas_p_value=gwas_p,
            gwas_beta=gwas_beta,
            gwas_trait=gwas_trait,
            gwas_posterior_prob=gwas_posterior,
            has_eqtl=has_eqtl,
            eqtl_beta=eqtl_beta,
            eqtl_p_value=eqtl_p,
            eqtl_tissue=eqtl_tissue,
            has_pqtl=has_pqtl,
            pqtl_beta=pqtl_beta,
            pqtl_p_value=pqtl_p,
            has_atac_peak=has_atac,
            atac_significance=atac_sig,
            n_disrupted_tfs=n_tfs,
            disrupted_tfs=disrupted_tfs,
            composite_score=composite,
            evidence_level=composite.get_evidence_level(),
            effect_direction=effect_dir,
            concordant=concordant
        )

    def calculate_composite_score(
        self,
        gwas_p: Optional[float] = None,
        gwas_beta: Optional[float] = None,
        gwas_posterior: Optional[float] = None,
        has_eqtl: bool = False,
        eqtl_beta: Optional[float] = None,
        has_pqtl: bool = False,
        pqtl_beta: Optional[float] = None,
        has_atac: bool = False,
        n_disrupted_tfs: int = 0,
        gwas_beta_concordant: bool = True
    ) -> CompositeScore:
        """
        Calculate composite score following Figure 5 framework.

        Scoring breakdown (max 55 points):
        - GWAS evidence: 0-10 points
        - QTL evidence: 0-15 points
        - TF disruption: 0-10 points
        - Expression change: 0-5 points
        - Protective evidence: 0-15 points

        Args:
            gwas_p: GWAS p-value
            gwas_beta: GWAS effect size
            gwas_posterior: GWAS posterior probability
            has_eqtl: Whether eQTL exists
            eqtl_beta: eQTL effect size
            has_pqtl: Whether pQTL exists
            pqtl_beta: pQTL effect size
            has_atac: Whether ATAC-seq peak exists
            n_disrupted_tfs: Number of disrupted TFs
            gwas_beta_concordant: Whether effects are concordant

        Returns:
            CompositeScore object with breakdown
        """
        # GWAS Evidence (0-10 points)
        gwas_score = 0.0
        if gwas_p is not None:
            if gwas_p < 5e-8:  # Genome-wide significant
                gwas_score += 5.0
            elif gwas_p < 1e-5:
                gwas_score += 3.0
            elif gwas_p < 0.001:
                gwas_score += 1.0

        if gwas_posterior is not None:
            if gwas_posterior > 0.1:
                gwas_score += 5.0
            elif gwas_posterior > 0.01:
                gwas_score += 3.0

        if gwas_beta is not None and abs(gwas_beta) > 0.05:
            gwas_score = min(gwas_score + 2.0, 10.0)

        gwas_score = min(gwas_score, 10.0)

        # QTL Evidence (0-15 points)
        qtl_score = 0.0
        if has_eqtl:
            qtl_score += 5.0
        if has_pqtl:
            qtl_score += 5.0

        # Concordance bonus (eQTL/pQTL direction matches GWAS)
        if gwas_beta_concordant and (has_eqtl or has_pqtl):
            qtl_score += 5.0

        qtl_score = min(qtl_score, 15.0)

        # TF Disruption (0-10 points)
        tf_score = 0.0
        if n_disrupted_tfs > 0:
            # Scale by number of TFs, max 10 points
            tf_score = min(n_disrupted_tfs * 2.0, 10.0)

        # Expression Change (0-5 points)
        expression_score = 0.0
        if eqtl_beta is not None:
            # Scale by effect size
            expression_score = min(abs(eqtl_beta) * 10.0, 5.0)

        # Protective Evidence (0-15 points)
        # This is determined by direction of effect
        protective_score = 0.0
        if gwas_beta is not None and gwas_beta < 0:  # Negative beta = protective
            # Higher score for stronger protective effects
            if abs(gwas_beta) > 0.1:
                protective_score = 15.0
            elif abs(gwas_beta) > 0.05:
                protective_score = 10.0
            else:
                protective_score = 5.0

        # ATAC-seq bonus (added to expression score)
        if has_atac:
            expression_score = min(expression_score + 2.0, 5.0)

        # Total score
        total = gwas_score + qtl_score + tf_score + expression_score + protective_score
        total = min(total, 55.0)

        return CompositeScore(
            gwas_score=gwas_score,
            qtl_score=qtl_score,
            tf_score=tf_score,
            expression_score=expression_score,
            protective_score=protective_score,
            total_score=total
        )

    def check_concordance(
        self,
        gwas_beta: Optional[float],
        eqtl_beta: Optional[float],
        pqtl_beta: Optional[float]
    ) -> bool:
        """
        Check if eQTL/pQTL effects are concordant with GWAS direction.

        Concordance means all effect directions agree (all positive or all negative).

        Args:
            gwas_beta: GWAS effect size
            eqtl_beta: eQTL effect size
            pqtl_beta: pQTL effect size

        Returns:
            True if concordant, False otherwise
        """
        # Collect non-None betas
        betas = [b for b in [gwas_beta, eqtl_beta, pqtl_beta] if b is not None]

        if len(betas) < 2:
            # Need at least 2 to check concordance
            return False

        # Check if all same sign
        signs = [np.sign(b) for b in betas]
        return len(set(signs)) == 1 and signs[0] != 0

    def _determine_effect_direction(
        self,
        gwas_beta: Optional[float]
    ) -> EffectDirection:
        """Determine effect direction from GWAS beta"""
        if gwas_beta is None:
            return EffectDirection.UNKNOWN

        if gwas_beta < -0.05:
            return EffectDirection.PROTECTIVE
        elif gwas_beta > 0.05:
            return EffectDirection.RISK
        else:
            return EffectDirection.NEUTRAL

    def analyze_snp_list(
        self,
        snp_ids: List[str],
        gene: str,
        gwas_df: Optional[pd.DataFrame] = None,
        eqtl_df: Optional[pd.DataFrame] = None,
        pqtl_df: Optional[pd.DataFrame] = None,
        atac_df: Optional[pd.DataFrame] = None
    ) -> List[GenomicsResult]:
        """
        Batch analysis for multiple SNPs associated with a gene.

        Args:
            snp_ids: List of SNP identifiers
            gene: Gene symbol
            gwas_df: DataFrame with GWAS data (indexed by SNP ID)
            eqtl_df: DataFrame with eQTL data (indexed by SNP ID)
            pqtl_df: DataFrame with pQTL data (indexed by SNP ID)
            atac_df: DataFrame with ATAC-seq data (indexed by SNP ID)

        Returns:
            List of GenomicsResult objects
        """
        results = []

        for snp_id in snp_ids:
            # Extract data for this SNP
            gwas_data = None
            if gwas_df is not None and snp_id in gwas_df.index:
                gwas_data = gwas_df.loc[snp_id].to_dict()

            eqtl_data = None
            if eqtl_df is not None and snp_id in eqtl_df.index:
                eqtl_data = eqtl_df.loc[snp_id].to_dict()

            pqtl_data = None
            if pqtl_df is not None and snp_id in pqtl_df.index:
                pqtl_data = pqtl_df.loc[snp_id].to_dict()

            atac_data = None
            if atac_df is not None and snp_id in atac_df.index:
                atac_data = atac_df.loc[snp_id].to_dict()

            # Analyze this SNP
            result = self.multi_modal_integration(
                snp_id=snp_id,
                gene=gene,
                gwas_data=gwas_data,
                eqtl_data=eqtl_data,
                pqtl_data=pqtl_data,
                atac_data=atac_data,
                fetch_missing=False  # Don't fetch, use provided data only
            )

            results.append(result)

        return results

    def rank_mechanisms(
        self,
        results: List[GenomicsResult],
        top_n: Optional[int] = None,
        min_score: float = 10.0
    ) -> List[MechanismRanking]:
        """
        Rank SNP-gene mechanisms by composite score.

        Args:
            results: List of GenomicsResult objects
            top_n: Number of top mechanisms to return (None = all)
            min_score: Minimum composite score threshold

        Returns:
            Sorted list of MechanismRanking objects
        """
        # Filter by minimum score
        filtered = [r for r in results if r.composite_score.total_score >= min_score]

        # Sort by total score (descending)
        sorted_results = sorted(
            filtered,
            key=lambda r: r.composite_score.total_score,
            reverse=True
        )

        # Limit to top N if specified
        if top_n is not None:
            sorted_results = sorted_results[:top_n]

        # Create rankings
        rankings = []
        for rank, result in enumerate(sorted_results, start=1):
            # Identify key evidence
            key_evidence = []
            if result.composite_score.gwas_score >= 5:
                key_evidence.append("Strong GWAS signal")
            if result.has_eqtl and result.has_pqtl:
                key_evidence.append("Both eQTL and pQTL")
            elif result.has_eqtl:
                key_evidence.append("eQTL evidence")
            elif result.has_pqtl:
                key_evidence.append("pQTL evidence")
            if result.concordant:
                key_evidence.append("Concordant effects")
            if result.n_disrupted_tfs > 0:
                key_evidence.append(f"{result.n_disrupted_tfs} TF disruptions")
            if result.effect_direction == EffectDirection.PROTECTIVE:
                key_evidence.append("Protective effect")

            ranking = MechanismRanking(
                snp_id=result.snp_id,
                gene=result.gene,
                total_score=result.composite_score.total_score,
                evidence_level=result.evidence_level,
                effect_direction=result.effect_direction,
                key_evidence=key_evidence,
                rank=rank
            )

            rankings.append(ranking)

        return rankings
