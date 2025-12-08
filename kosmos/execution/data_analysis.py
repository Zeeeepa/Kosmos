"""
Data analysis pipeline implementing proven patterns from kosmos-figures.

This module provides the DataAnalyzer class with statistical analysis methods
extracted directly from kosmos-figures repository analysis scripts.

References:
- Figure 2 (hypothermia_nucleotide_salvage): T-test comparison pattern
- Figure 3 (perovskite_solar_cell): Correlation analysis pattern
- Figure 4 (neural_network): Log-log scaling analysis pattern
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional, Union, Any
import logging
from pathlib import Path
import warnings

# Suppress scientific computation warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """
    Reusable analysis methods extracted from kosmos-figures.

    Implements proven statistical patterns:
    - T-test comparison (group mean differences)
    - Correlation analysis (Pearson and Spearman)
    - Linear regression with significance testing
    - Log-log scaling analysis for power laws
    """

    def __init__(self):
        """Initialize DataAnalyzer."""
        self.results_cache = {}

    @staticmethod
    def ttest_comparison(
        data: pd.DataFrame,
        group_col: str,
        measure_col: str,
        groups: Tuple[str, str],
        log_transform: bool = False
    ) -> Dict[str, Any]:
        """
        Perform t-test comparison between two groups.

        Pattern from: Figure_2_hypothermia_nucleotide_salvage

        Args:
            data: DataFrame with group assignments and measurements
            group_col: Column name containing group labels
            measure_col: Column name containing measurements to compare
            groups: Tuple of (group1_label, group2_label) to compare
            log_transform: If True, apply log2 transformation before comparison

        Returns:
            Dictionary with:
                - t_statistic: T-test statistic
                - p_value: P-value for the test
                - group1_mean: Mean of group 1
                - group2_mean: Mean of group 2
                - group1_std: Standard deviation of group 1
                - group2_std: Standard deviation of group 2
                - mean_difference: group1_mean - group2_mean
                - log2_fold_change: log2(group1_mean / group2_mean)
                - significant_0.05: Boolean, p < 0.05
                - significant_0.01: Boolean, p < 0.01
                - significant_0.001: Boolean, p < 0.001
                - significance_label: '***', '**', '*', or 'ns'
                - n_group1: Sample size group 1
                - n_group2: Sample size group 2

        Example:
            >>> df = pd.DataFrame({
            ...     'treatment': ['control']*30 + ['experimental']*30,
            ...     'score': np.concatenate([np.random.normal(10, 2, 30),
            ...                              np.random.normal(12, 2, 30)])
            ... })
            >>> result = DataAnalyzer.ttest_comparison(
            ...     df, 'treatment', 'score', ('experimental', 'control')
            ... )
            >>> print(f"P-value: {result['p_value']:.4f}")
        """
        # Extract group data
        group1_data = data[data[group_col] == groups[0]][measure_col].dropna()
        group2_data = data[data[group_col] == groups[1]][measure_col].dropna()

        # Validate data
        if len(group1_data) == 0 or len(group2_data) == 0:
            raise ValueError(f"One or both groups have no data. "
                           f"Group '{groups[0]}': {len(group1_data)} samples, "
                           f"Group '{groups[1]}': {len(group2_data)} samples")

        # Log transformation if requested (kosmos-figures Figure 2 pattern)
        if log_transform:
            # Add 1 to avoid log(0)
            group1_data = np.log2(group1_data + 1)
            group2_data = np.log2(group2_data + 1)

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(group1_data, group2_data)

        # Calculate statistics
        group1_mean = np.mean(group1_data)
        group2_mean = np.mean(group2_data)
        mean_diff = group1_mean - group2_mean

        # Log2 fold change (handle division by zero)
        if group2_mean != 0:
            log2_fc = np.log2(group1_mean / group2_mean) if group1_mean > 0 and group2_mean > 0 else np.nan
        else:
            log2_fc = np.nan

        # Significance thresholds (kosmos-figures standard)
        sig_0_05 = p_value < 0.05
        sig_0_01 = p_value < 0.01
        sig_0_001 = p_value < 0.001

        # Significance label
        if sig_0_001:
            sig_label = "***"
        elif sig_0_01:
            sig_label = "**"
        elif sig_0_05:
            sig_label = "*"
        else:
            sig_label = "ns"

        return {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'group1_mean': float(group1_mean),
            'group2_mean': float(group2_mean),
            'group1_std': float(np.std(group1_data, ddof=1)),
            'group2_std': float(np.std(group2_data, ddof=1)),
            'mean_difference': float(mean_diff),
            'log2_fold_change': float(log2_fc) if not np.isnan(log2_fc) else None,
            'significant_0.05': bool(sig_0_05),
            'significant_0.01': bool(sig_0_01),
            'significant_0.001': bool(sig_0_001),
            'significance_label': sig_label,
            'n_group1': int(len(group1_data)),
            'n_group2': int(len(group2_data))
        }

    @staticmethod
    def correlation_analysis(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        method: str = 'pearson'
    ) -> Dict[str, Any]:
        """
        Perform correlation analysis with linear regression.

        Pattern from: Figure_3_perovskite_solar_cell

        Args:
            data: DataFrame with variables to correlate
            x_col: Column name for x variable
            y_col: Column name for y variable
            method: 'pearson' or 'spearman' correlation

        Returns:
            Dictionary with:
                - correlation: Correlation coefficient
                - p_value: P-value for correlation test
                - r_squared: Coefficient of determination (R²)
                - slope: Linear regression slope
                - intercept: Linear regression intercept
                - std_err: Standard error of the regression
                - significance: '***', '**', '*', or 'ns'
                - n_samples: Number of samples used
                - equation: Regression equation string

        Example:
            >>> df = pd.DataFrame({
            ...     'x': np.random.randn(100),
            ...     'y': np.random.randn(100)
            ... })
            >>> result = DataAnalyzer.correlation_analysis(df, 'x', 'y')
            >>> print(f"r = {result['correlation']:.3f}, p = {result['p_value']:.4f}")
        """
        # Remove missing values (kosmos-figures pattern)
        df_clean = data[[x_col, y_col]].dropna()

        if len(df_clean) < 3:
            raise ValueError(f"Insufficient data after removing NaN values. "
                           f"Need at least 3 samples, got {len(df_clean)}")

        x = df_clean[x_col].values
        y = df_clean[y_col].values

        # Correlation
        if method == 'pearson':
            corr, p_val = stats.pearsonr(x, y)
        elif method == 'spearman':
            corr, p_val = stats.spearmanr(x, y)
        else:
            raise ValueError(f"Unknown method '{method}'. Use 'pearson' or 'spearman'")

        # Linear regression (always use for equation regardless of correlation method)
        slope, intercept, r_value, p_value_reg, std_err = stats.linregress(x, y)

        # Significance label (kosmos-figures pattern)
        if p_val < 0.001:
            significance = "***"
        elif p_val < 0.01:
            significance = "**"
        elif p_val < 0.05:
            significance = "*"
        else:
            significance = "ns"

        # Regression equation
        sign = "+" if intercept >= 0 else ""
        equation = f"y = {slope:.4f}x {sign}{intercept:.4f}"

        return {
            'correlation': float(corr),
            'p_value': float(p_val),
            'r_squared': float(r_value ** 2),
            'slope': float(slope),
            'intercept': float(intercept),
            'std_err': float(std_err),
            'significance': significance,
            'n_samples': int(len(x)),
            'equation': equation,
            'method': method
        }

    @staticmethod
    def log_log_scaling_analysis(
        data: pd.DataFrame,
        x_col: str,
        y_col: str
    ) -> Dict[str, Any]:
        """
        Analyze scaling relationships on log-log scale.

        Pattern from: Figure_4_neural_network (connectomics scaling laws)

        Fits a power law: y = a * x^b

        Args:
            data: DataFrame with variables to analyze
            x_col: Column name for x variable
            y_col: Column name for y variable

        Returns:
            Dictionary with:
                - spearman_rho: Spearman correlation coefficient
                - p_value: P-value for Spearman correlation
                - power_law_exponent: Exponent b in y = a * x^b
                - power_law_coefficient: Coefficient a in y = a * x^b
                - r_squared: R² of log-log linear fit
                - equation: Power law equation string
                - n_samples: Number of samples used
                - log_log_slope: Slope of log-log regression
                - log_log_intercept: Intercept of log-log regression

        Example:
            >>> df = pd.DataFrame({
            ...     'length': np.random.uniform(1, 100, 100),
            ...     'synapses': np.random.uniform(1, 100, 100)
            ... })
            >>> result = DataAnalyzer.log_log_scaling_analysis(df, 'length', 'synapses')
            >>> print(result['equation'])
        """
        # Clean data - remove NaN and non-positive values (kosmos-figures pattern)
        df_clean = data[[x_col, y_col]].dropna()
        df_clean = df_clean[(df_clean[x_col] > 0) & (df_clean[y_col] > 0)]

        if len(df_clean) < 3:
            raise ValueError(f"Insufficient positive data for log-log analysis. "
                           f"Need at least 3 positive samples, got {len(df_clean)}")

        x = df_clean[x_col].values
        y = df_clean[y_col].values

        # Log-transform
        log_x = np.log10(x)
        log_y = np.log10(y)

        # Spearman correlation (non-parametric, kosmos-figures standard)
        rho, p_value = stats.spearmanr(x, y)

        # Linear fit on log-log scale: log(y) = log(a) + b*log(x)
        # This gives power law: y = a * x^b
        slope, intercept, r_value, p_value_reg, std_err = stats.linregress(log_x, log_y)

        # Convert back to power law parameters
        # log(y) = log(a) + b*log(x)  =>  y = 10^intercept * x^slope
        a = 10 ** intercept  # power_law_coefficient
        b = slope  # power_law_exponent

        # Power law equation
        equation = f"y = {a:.3f} * x^{b:.3f}"

        return {
            'spearman_rho': float(rho),
            'p_value': float(p_value),
            'power_law_exponent': float(b),
            'power_law_coefficient': float(a),
            'r_squared': float(r_value ** 2),
            'equation': equation,
            'n_samples': int(len(x)),
            'log_log_slope': float(slope),
            'log_log_intercept': float(intercept)
        }

    @staticmethod
    def anova_comparison(
        data: pd.DataFrame,
        group_col: str,
        measure_col: str,
        groups: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform one-way ANOVA for multiple group comparison.

        Args:
            data: DataFrame with group assignments and measurements
            group_col: Column name containing group labels
            measure_col: Column name containing measurements to compare
            groups: Optional list of specific groups to compare (default: all unique groups)

        Returns:
            Dictionary with:
                - f_statistic: F-statistic
                - p_value: P-value for ANOVA
                - group_means: Dict of {group: mean} for each group
                - group_stds: Dict of {group: std} for each group
                - group_sizes: Dict of {group: n} for each group
                - significant_0.05: Boolean, p < 0.05
                - eta_squared: Effect size (η²)
                - between_group_variance: Variance between groups
                - within_group_variance: Variance within groups
        """
        # Filter groups if specified
        if groups is not None:
            data = data[data[group_col].isin(groups)]

        # Get unique groups
        unique_groups = data[group_col].unique()

        if len(unique_groups) < 2:
            raise ValueError(f"Need at least 2 groups for ANOVA, got {len(unique_groups)}")

        # Prepare data for each group
        group_data = [data[data[group_col] == g][measure_col].dropna() for g in unique_groups]

        # Validate all groups have data
        for i, gd in enumerate(group_data):
            if len(gd) == 0:
                raise ValueError(f"Group '{unique_groups[i]}' has no data")

        # Perform one-way ANOVA
        f_stat, p_value = stats.f_oneway(*group_data)

        # Calculate group statistics
        group_means = {str(g): float(np.mean(gd)) for g, gd in zip(unique_groups, group_data)}
        group_stds = {str(g): float(np.std(gd, ddof=1)) for g, gd in zip(unique_groups, group_data)}
        group_sizes = {str(g): int(len(gd)) for g, gd in zip(unique_groups, group_data)}

        # Calculate effect size (eta-squared)
        grand_mean = np.mean(np.concatenate(group_data))
        ss_between = sum(len(gd) * (np.mean(gd) - grand_mean) ** 2 for gd in group_data)
        ss_total = sum((x - grand_mean) ** 2 for gd in group_data for x in gd)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0

        # Variance components
        between_var = np.var([np.mean(gd) for gd in group_data], ddof=1)
        within_var = np.mean([np.var(gd, ddof=1) for gd in group_data])

        return {
            'f_statistic': float(f_stat),
            'p_value': float(p_value),
            'group_means': group_means,
            'group_stds': group_stds,
            'group_sizes': group_sizes,
            'significant_0.05': bool(p_value < 0.05),
            'significant_0.01': bool(p_value < 0.01),
            'eta_squared': float(eta_squared),
            'between_group_variance': float(between_var),
            'within_group_variance': float(within_var),
            'n_groups': int(len(unique_groups))
        }

    @staticmethod
    def shap_feature_importance(
        model,
        X_train: Union[pd.DataFrame, np.ndarray],
        X_test: Optional[Union[pd.DataFrame, np.ndarray]] = None,
        max_display: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate SHAP values for feature importance explanation (REQ-DAA-CAP-005).

        SHAP (SHapley Additive exPlanations) provides unified measure of feature
        importance based on cooperative game theory.

        Args:
            model: Trained sklearn model (tree-based models work best)
            X_train: Training data for background distribution
            X_test: Test data to explain (if None, uses X_train sample)
            max_display: Maximum features to include in results

        Returns:
            Dictionary with:
                - feature_importance: Dict of {feature: importance}
                - shap_values: SHAP values array
                - base_value: Expected model output
                - feature_names: List of feature names

        Example:
            >>> from sklearn.ensemble import RandomForestClassifier
            >>> model = RandomForestClassifier().fit(X_train, y_train)
            >>> result = DataAnalyzer.shap_feature_importance(model, X_train, X_test)
            >>> print(result['feature_importance'])
        """
        try:
            import shap
        except ImportError:
            raise ImportError("shap package required. Install with: pip install shap")

        # Convert to DataFrame if numpy array
        if isinstance(X_train, np.ndarray):
            X_train = pd.DataFrame(X_train, columns=[f'feature_{i}' for i in range(X_train.shape[1])])

        if X_test is None:
            # Sample from training data
            X_test = X_train.sample(min(100, len(X_train)))
        elif isinstance(X_test, np.ndarray):
            X_test = pd.DataFrame(X_test, columns=X_train.columns)

        # Create explainer (TreeExplainer for tree models, otherwise KernelExplainer)
        try:
            explainer = shap.TreeExplainer(model)
        except Exception:
            # Fallback to KernelExplainer for non-tree models
            explainer = shap.KernelExplainer(model.predict, shap.sample(X_train, 100))

        # Calculate SHAP values
        shap_values = explainer.shap_values(X_test)

        # Handle multi-output case (classification with >2 classes)
        if isinstance(shap_values, list):
            # Use first class for importance ranking
            shap_values_importance = np.abs(shap_values[0]).mean(axis=0)
        else:
            shap_values_importance = np.abs(shap_values).mean(axis=0)

        # Create feature importance dictionary
        feature_importance = dict(zip(
            X_train.columns,
            shap_values_importance
        ))

        # Sort by importance
        feature_importance = dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:max_display])

        return {
            'feature_importance': {k: float(v) for k, v in feature_importance.items()},
            'base_value': float(explainer.expected_value if not isinstance(explainer.expected_value, list) else explainer.expected_value[0]),
            'feature_names': list(X_train.columns),
            'n_samples': int(len(X_test))
        }

    @staticmethod
    def pathway_enrichment_analysis(
        gene_list: List[str],
        organism: str = 'human',
        gene_sets: str = 'KEGG_2021_Human',
        outdir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform pathway enrichment analysis using gseapy (REQ-DAA-CAP-008).

        Identifies biological pathways that are over-represented in gene list.

        Args:
            gene_list: List of gene symbols
            organism: Species ('human', 'mouse', etc.)
            gene_sets: Gene set library (KEGG, GO, Reactome, etc.)
            outdir: Output directory for plots (optional)

        Returns:
            Dictionary with:
                - enriched_pathways: List of enriched pathways
                - top_pathway: Most significant pathway
                - significant_count: Number of significant pathways
                - results_table: Full results as dict

        Example:
            >>> genes = ['BRCA1', 'TP53', 'EGFR', 'KRAS']
            >>> result = DataAnalyzer.pathway_enrichment_analysis(genes)
            >>> print(result['top_pathway'])
        """
        try:
            import gseapy as gp
        except ImportError:
            raise ImportError("gseapy package required. Install with: pip install gseapy")

        # Run enrichment analysis
        enr = gp.enrichr(
            gene_list=gene_list,
            gene_sets=gene_sets,
            organism=organism.capitalize(),
            outdir=outdir,
            no_plot=True if outdir is None else False,
            cutoff=0.05  # Adjusted p-value cutoff
        )

        results_df = enr.results

        # Extract significant pathways
        significant = results_df[results_df['Adjusted P-value'] < 0.05]

        enriched_pathways = []
        for _, row in significant.iterrows():
            enriched_pathways.append({
                'pathway': row['Term'],
                'p_value': float(row['P-value']),
                'adj_p_value': float(row['Adjusted P-value']),
                'genes': row['Genes'].split(';') if isinstance(row['Genes'], str) else [],
                'n_genes': int(row['Overlap'].split('/')[0]) if '/' in str(row['Overlap']) else 0
            })

        return {
            'enriched_pathways': enriched_pathways,
            'top_pathway': enriched_pathways[0] if enriched_pathways else None,
            'significant_count': len(enriched_pathways),
            'total_tested': len(results_df)
        }

    @staticmethod
    def fit_distributions(
        data: pd.Series,
        distributions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fit multiple statistical distributions and find best fit (REQ-DAA-CAP-005).

        Args:
            data: Data to fit
            distributions: List of distribution names (default: common distributions)

        Returns:
            Dictionary with:
                - best_fit: Best distribution name
                - best_params: Parameters of best distribution
                - aic_scores: AIC scores for all distributions
                - ks_test: Kolmogorov-Smirnov test results

        Example:
            >>> data = pd.Series(np.random.lognormal(0, 1, 1000))
            >>> result = DataAnalyzer.fit_distributions(data)
            >>> print(f"Best fit: {result['best_fit']}")
        """
        if distributions is None:
            distributions = ['norm', 'lognorm', 'gamma', 'expon', 'weibull_min']

        # Remove NaN values
        data_clean = data.dropna()

        results = {}
        best_aic = float('inf')
        best_dist = None
        best_params = None

        for dist_name in distributions:
            try:
                dist = getattr(stats, dist_name)

                # Fit distribution
                params = dist.fit(data_clean)

                # Calculate AIC (Akaike Information Criterion)
                log_likelihood = np.sum(dist.logpdf(data_clean, *params))
                k = len(params)  # Number of parameters
                aic = 2 * k - 2 * log_likelihood

                # Kolmogorov-Smirnov test
                ks_stat, ks_pvalue = stats.kstest(data_clean, dist_name, args=params)

                results[dist_name] = {
                    'params': params,
                    'aic': float(aic),
                    'ks_statistic': float(ks_stat),
                    'ks_pvalue': float(ks_pvalue)
                }

                if aic < best_aic:
                    best_aic = aic
                    best_dist = dist_name
                    best_params = params

            except Exception as e:
                logger.debug(f"Failed to fit {dist_name}: {e}")
                continue

        return {
            'best_fit': best_dist,
            'best_params': list(best_params) if best_params else None,
            'aic_scores': {k: v['aic'] for k, v in results.items()},
            'all_results': results
        }

    @staticmethod
    def segmented_regression(
        x: Union[pd.Series, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        n_breakpoints: int = 1
    ) -> Dict[str, Any]:
        """
        Perform piecewise linear (segmented) regression (REQ-DAA-CAP-005).

        Fits multiple linear segments to data, useful for identifying regime changes.

        Args:
            x: Independent variable
            y: Dependent variable
            n_breakpoints: Number of breakpoints (segments = breakpoints + 1)

        Returns:
            Dictionary with:
                - breakpoints: List of breakpoint locations
                - slopes: Slope of each segment
                - intercepts: Intercept of each segment
                - r_squared: R² of the fit

        Example:
            >>> x = np.array([1, 2, 3, 4, 5, 6, 7, 8])
            >>> y = np.array([1, 2, 3, 3.5, 4, 5, 6, 7])  # Change at x=4
            >>> result = DataAnalyzer.segmented_regression(x, y, n_breakpoints=1)
            >>> print(f"Breakpoint at x={result['breakpoints'][0]:.2f}")
        """
        try:
            import pwlf
        except ImportError:
            raise ImportError("pwlf package required. Install with: pip install pwlf")

        # Convert to numpy arrays
        if isinstance(x, pd.Series):
            x = x.values
        if isinstance(y, pd.Series):
            y = y.values

        # Initialize piecewise linear fit
        model = pwlf.PiecewiseLinFit(x, y)

        # Fit model
        breakpoints = model.fit(n_breakpoints + 1)  # +1 because includes endpoints

        # Get slopes and intercepts for each segment
        slopes = model.calc_slopes()
        intercepts = []

        # Calculate R²
        y_pred = model.predict(x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        return {
            'breakpoints': [float(bp) for bp in breakpoints[1:-1]],  # Exclude endpoints
            'slopes': [float(s) for s in slopes],
            'r_squared': float(r_squared),
            'prediction_function': lambda x_new: model.predict(x_new)
        }

    @staticmethod
    def create_publication_plot(
        data: Union[pd.DataFrame, Dict[str, Any]],
        plot_type: str,
        output_path: str,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate publication-quality plots (REQ-DAA-CAP-006).

        Args:
            data: Data to plot (DataFrame or dict)
            plot_type: Type of plot ('scatter', 'boxplot', 'heatmap', 'distribution', 'bar')
            output_path: Path to save figure
            title: Plot title
            **kwargs: Additional plot-specific parameters

        Returns:
            str: Path to saved figure

        Example:
            >>> df = pd.DataFrame({'x': [1,2,3,4], 'y': [2,4,6,8]})
            >>> path = DataAnalyzer.create_publication_plot(
            ...     df, 'scatter', 'output.png',
            ...     x='x', y='y', title='My Plot'
            ... )
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Set publication-quality style
        sns.set_style('whitegrid')
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 11
        plt.rcParams['ytick.labelsize'] = 11
        plt.rcParams['legend.fontsize'] = 11
        plt.rcParams['figure.dpi'] = 300

        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (8, 6)))

        if plot_type == 'scatter':
            x_col = kwargs.get('x')
            y_col = kwargs.get('y')
            if isinstance(data, pd.DataFrame):
                ax.scatter(data[x_col], data[y_col], alpha=0.6)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

        elif plot_type == 'boxplot':
            if isinstance(data, pd.DataFrame):
                data.boxplot(ax=ax, **{k: v for k, v in kwargs.items() if k not in ['figsize']})

        elif plot_type == 'heatmap':
            if isinstance(data, pd.DataFrame):
                sns.heatmap(data, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)

        elif plot_type == 'distribution':
            values = kwargs.get('values')
            if values is not None:
                ax.hist(values, bins=kwargs.get('bins', 30), alpha=0.7, edgecolor='black')
                ax.set_xlabel(kwargs.get('xlabel', 'Value'))
                ax.set_ylabel(kwargs.get('ylabel', 'Frequency'))

        elif plot_type == 'bar':
            x_col = kwargs.get('x')
            y_col = kwargs.get('y')
            if isinstance(data, pd.DataFrame):
                data.plot(x=x_col, y=y_col, kind='bar', ax=ax, legend=False)

        if title:
            ax.set_title(title)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved publication plot to {output_path}")
        return output_path

    @staticmethod
    def save_to_notebook(
        analysis_results: Dict[str, Any],
        output_path: str,
        title: str = "Data Analysis Results"
    ) -> str:
        """
        Save analysis results to Jupyter notebook format (REQ-DAA-SUM-004).

        Each statement should cite a Jupyter notebook for traceability.

        Args:
            analysis_results: Dictionary containing analysis results
            output_path: Path to save .ipynb file
            title: Notebook title

        Returns:
            str: Path to saved notebook

        Example:
            >>> results = {'mean': 5.0, 'std': 1.2, 'p_value': 0.03}
            >>> path = DataAnalyzer.save_to_notebook(
            ...     results, 'analysis.ipynb', 'Statistical Analysis'
            ... )
        """
        try:
            import nbformat
            from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
        except ImportError:
            raise ImportError("nbformat required. Install with: pip install nbformat")

        # Create new notebook
        nb = new_notebook()

        # Add title cell
        nb.cells.append(new_markdown_cell(f"# {title}\n\nGenerated by Kosmos AI Scientist"))

        # Add results as code cells with outputs
        for key, value in analysis_results.items():
            # Create code that produces the result
            code = f"# {key}\nresult = {repr(value)}\nprint(result)"

            cell = new_code_cell(code)
            # Add output
            cell.outputs = [{
                'output_type': 'stream',
                'name': 'stdout',
                'text': str(value)
            }]
            nb.cells.append(cell)

        # Save notebook
        with open(output_path, 'w') as f:
            nbformat.write(nb, f)

        logger.info(f"Saved analysis notebook to {output_path}")
        return output_path


class DataLoader:
    """
    Utility class for loading data from various formats.

    Supports CSV, Excel, JSON with automatic type detection and validation.
    """

    @staticmethod
    def load_csv(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Load CSV file with pandas.

        Args:
            file_path: Path to CSV file
            **kwargs: Additional arguments to pass to pd.read_csv()

        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading CSV from {file_path}")
        df = pd.read_csv(file_path, **kwargs)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df

    @staticmethod
    def load_excel(file_path: Union[str, Path], sheet_name: Union[str, int] = 0, **kwargs) -> pd.DataFrame:
        """
        Load Excel file with pandas.

        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index to load
            **kwargs: Additional arguments to pass to pd.read_excel()

        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading Excel from {file_path}, sheet: {sheet_name}")
        df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df

    @staticmethod
    def load_json(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Load JSON file with pandas.

        Args:
            file_path: Path to JSON file
            **kwargs: Additional arguments to pass to pd.read_json()

        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading JSON from {file_path}")
        df = pd.read_json(file_path, **kwargs)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df

    @staticmethod
    def load_h5ad(
        file_path: Union[str, Path],
        to_dataframe: bool = True,
        obs_columns: Optional[List[str]] = None,
        var_columns: Optional[List[str]] = None,
        **kwargs
    ) -> Union[pd.DataFrame, Any]:
        """
        Load h5ad file (single-cell RNA-seq data format).

        h5ad is the standard format for single-cell RNA-seq data, used by
        scanpy and other single-cell analysis tools. It stores gene expression
        matrices along with cell metadata (obs) and gene metadata (var).

        Args:
            file_path: Path to h5ad file
            to_dataframe: If True, return expression matrix as DataFrame.
                         If False, return the full AnnData object.
            obs_columns: List of cell metadata columns to include (default: all)
            var_columns: List of gene metadata columns to include (default: all)
            **kwargs: Additional arguments to pass to anndata.read_h5ad()

        Returns:
            If to_dataframe=True: DataFrame with gene expression data
            If to_dataframe=False: AnnData object with full structure

        Example:
            >>> df = DataLoader.load_h5ad('single_cell_data.h5ad')
            >>> print(f"Loaded {df.shape[0]} cells x {df.shape[1]} genes")

        Note:
            Requires anndata package: pip install anndata
            For full analysis capabilities, also install scanpy: pip install scanpy
        """
        try:
            import anndata
        except ImportError:
            raise ImportError(
                "anndata package required for h5ad files. "
                "Install with: pip install anndata "
                "or: pip install kosmos-ai-scientist[science]"
            )

        logger.info(f"Loading h5ad from {file_path}")
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"h5ad file not found: {file_path}")

        # Load AnnData object
        adata = anndata.read_h5ad(file_path, **kwargs)
        logger.info(f"Loaded AnnData: {adata.n_obs} cells x {adata.n_vars} genes")

        if not to_dataframe:
            return adata

        # Convert to DataFrame
        # Expression matrix (cells x genes)
        if hasattr(adata.X, 'toarray'):
            # Sparse matrix - convert to dense
            expr_matrix = adata.X.toarray()
        else:
            expr_matrix = adata.X

        df = pd.DataFrame(
            expr_matrix,
            index=adata.obs_names,
            columns=adata.var_names
        )

        # Optionally add cell metadata columns
        if obs_columns is not None:
            for col in obs_columns:
                if col in adata.obs.columns:
                    df[f"obs_{col}"] = adata.obs[col].values
        elif adata.obs.shape[1] > 0:
            # Add all obs columns with prefix
            for col in adata.obs.columns:
                df[f"obs_{col}"] = adata.obs[col].values

        logger.info(f"Converted to DataFrame: {df.shape[0]} rows x {df.shape[1]} columns")
        return df

    @staticmethod
    def load_parquet(
        file_path: Union[str, Path],
        columns: Optional[List[str]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load Parquet file (columnar data format).

        Parquet is an efficient columnar storage format commonly used for
        large-scale analytics data. It provides excellent compression and
        fast column-wise access.

        Args:
            file_path: Path to Parquet file
            columns: Specific columns to load (default: all columns)
            **kwargs: Additional arguments to pass to pandas.read_parquet()

        Returns:
            DataFrame with loaded data

        Example:
            >>> df = DataLoader.load_parquet('analytics_data.parquet')
            >>> df_subset = DataLoader.load_parquet('data.parquet', columns=['col1', 'col2'])

        Note:
            Requires pyarrow package: pip install pyarrow
            or: pip install kosmos-ai-scientist[science]
        """
        try:
            import pyarrow.parquet as pq
        except ImportError:
            raise ImportError(
                "pyarrow package required for Parquet files. "
                "Install with: pip install pyarrow "
                "or: pip install kosmos-ai-scientist[science]"
            )

        logger.info(f"Loading Parquet from {file_path}")
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {file_path}")

        # Read parquet file
        if columns is not None:
            df = pd.read_parquet(file_path, columns=columns, **kwargs)
        else:
            df = pd.read_parquet(file_path, **kwargs)

        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df

    @staticmethod
    def load_data(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Auto-detect file type and load data.

        Args:
            file_path: Path to data file
            **kwargs: Additional arguments to pass to loader

        Returns:
            DataFrame with loaded data

        Raises:
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix == '.csv':
            return DataLoader.load_csv(file_path, **kwargs)
        elif suffix in ['.xlsx', '.xls']:
            return DataLoader.load_excel(file_path, **kwargs)
        elif suffix == '.json':
            return DataLoader.load_json(file_path, **kwargs)
        elif suffix == '.h5ad':
            return DataLoader.load_h5ad(file_path, **kwargs)
        elif suffix == '.parquet':
            return DataLoader.load_parquet(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file type: {suffix}. "
                           f"Supported: .csv, .xlsx, .xls, .json, .h5ad, .parquet")


class DataCleaner:
    """
    Utility class for data cleaning and preprocessing.

    Implements common data cleaning patterns from kosmos-figures.
    """

    @staticmethod
    def remove_missing(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Remove rows with missing values.

        Args:
            df: DataFrame to clean
            subset: Optional list of columns to check for NaN (default: all columns)

        Returns:
            DataFrame with missing values removed
        """
        initial_rows = len(df)
        df_clean = df.dropna(subset=subset)
        removed = initial_rows - len(df_clean)

        if removed > 0:
            logger.info(f"Removed {removed} rows with missing values ({removed/initial_rows*100:.1f}%)")

        return df_clean

    @staticmethod
    def filter_positive(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Filter to keep only rows where specified columns have positive values.

        Pattern from: Figure_4_neural_network (log-log analysis requires positive values)

        Args:
            df: DataFrame to filter
            columns: Columns that must be positive

        Returns:
            DataFrame with only positive values in specified columns
        """
        initial_rows = len(df)

        for col in columns:
            df = df[df[col] > 0]

        removed = initial_rows - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} rows with non-positive values in {columns} "
                       f"({removed/initial_rows*100:.1f}%)")

        return df

    @staticmethod
    def remove_outliers(
        df: pd.DataFrame,
        column: str,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers using IQR or Z-score method.

        Args:
            df: DataFrame to clean
            column: Column to check for outliers
            method: 'iqr' (interquartile range) or 'zscore'
            threshold: IQR multiplier (default 1.5) or Z-score threshold (default 1.5)

        Returns:
            DataFrame with outliers removed
        """
        initial_rows = len(df)

        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            df_clean = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(df[column]))
            df_clean = df[z_scores < threshold]

        else:
            raise ValueError(f"Unknown method '{method}'. Use 'iqr' or 'zscore'")

        removed = initial_rows - len(df_clean)
        if removed > 0:
            logger.info(f"Removed {removed} outliers from '{column}' using {method} "
                       f"({removed/initial_rows*100:.1f}%)")

        return df_clean

    @staticmethod
    def normalize(df: pd.DataFrame, columns: List[str], method: str = 'zscore') -> pd.DataFrame:
        """
        Normalize specified columns.

        Args:
            df: DataFrame to normalize
            columns: Columns to normalize
            method: 'zscore' (standardize) or 'minmax' (scale to 0-1)

        Returns:
            DataFrame with normalized columns
        """
        df_normalized = df.copy()

        for col in columns:
            if method == 'zscore':
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    df_normalized[col] = (df[col] - mean) / std
                else:
                    logger.warning(f"Column '{col}' has zero variance, skipping normalization")

            elif method == 'minmax':
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df_normalized[col] = (df[col] - min_val) / (max_val - min_val)
                else:
                    logger.warning(f"Column '{col}' has constant value, skipping normalization")

            else:
                raise ValueError(f"Unknown method '{method}'. Use 'zscore' or 'minmax'")

        return df_normalized
