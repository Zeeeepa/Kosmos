"""
Materials Optimization and Parameter Analysis

Based on kosmos-figures Figure 3 pattern (Perovskite Solar Cell Optimization):
- Parameter-performance correlation analysis
- Multi-parameter optimization with surrogate modeling
- SHAP feature importance for explainable AI
- Design of Experiments (DoE) using Latin Hypercube Sampling

Example workflow:
    analyzer = MaterialsOptimizer()

    # Correlation analysis (Figure 3 pattern)
    result = analyzer.correlation_analysis(
        data=perovskite_df,
        parameter='Spin coater: Solvent Partial Pressure [ppm]',
        metric='Short circuit current density, Jsc [mA/cm2]'
    )
    # Returns: correlation=-0.708, p_value<0.001, significance='***'

    # SHAP analysis for feature importance
    shap_result = analyzer.shap_analysis(
        data=perovskite_df,
        features=['Pressure', 'Temperature', 'Time'],
        target='Jsc'
    )

    # Optimize parameters
    optimal = analyzer.parameter_space_optimization(
        data=perovskite_df,
        parameters=['Pressure', 'Temperature'],
        objective='Jsc',
        maximize=True
    )
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import differential_evolution
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


# Pydantic models for results

class CorrelationResult(BaseModel):
    """Result from parameter-performance correlation analysis"""
    parameter: str
    metric: str
    correlation: float  # Pearson correlation coefficient
    p_value: float
    r_squared: float
    slope: float
    intercept: float
    std_err: float
    significance: str  # "***" (p<0.001), "**" (p<0.01), "*" (p<0.05), "ns"
    n_samples: int
    equation: str  # Linear regression equation
    clean_data: Optional[pd.DataFrame] = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SHAPResult(BaseModel):
    """Result from SHAP feature importance analysis"""
    feature_importance: Dict[str, float]  # feature name -> mean absolute SHAP value
    shap_values: Optional[np.ndarray] = Field(default=None, exclude=True)
    model_r_squared: float
    model_type: str  # "RandomForest" or "XGBoost"
    n_features: int
    n_samples: int
    top_features: List[str] = Field(default_factory=list)  # Top 5 by importance

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OptimizationResult(BaseModel):
    """Result from parameter space optimization"""
    optimal_parameters: Dict[str, float]
    predicted_value: float
    optimization_success: bool
    n_iterations: int
    convergence_message: str
    parameter_bounds: Dict[str, Tuple[float, float]]
    model_r_squared: float

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DOEResult(BaseModel):
    """Result from Design of Experiments"""
    experiment_design: pd.DataFrame  # Sampled parameter combinations
    n_experiments: int
    n_parameters: int
    sampling_method: str  # "LatinHypercube" or "Random"
    parameter_ranges: Dict[str, Tuple[float, float]]

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Main analyzer class

class MaterialsOptimizer:
    """
    Materials optimization and parameter analysis.

    Provides methods for:
    - Correlation analysis (Figure 3 pattern from kosmos-figures)
    - SHAP-based feature importance
    - Multi-parameter optimization
    - Design of Experiments
    """

    def __init__(self):
        """Initialize MaterialsOptimizer."""
        pass

    def correlation_analysis(
        self,
        data: pd.DataFrame,
        parameter: str,
        metric: str,
        min_samples: int = 10
    ) -> CorrelationResult:
        """
        Analyze correlation between a parameter and performance metric.

        Based on Figure 3 pattern: Linear regression with Pearson correlation.

        Args:
            data: DataFrame with experimental data
            parameter: Column name for independent variable (e.g., 'Pressure')
            metric: Column name for dependent variable (e.g., 'Jsc')
            min_samples: Minimum samples required for analysis

        Returns:
            CorrelationResult with correlation, p-value, regression info

        Example:
            >>> result = analyzer.correlation_analysis(
            ...     data=df,
            ...     parameter='Spin coater: Solvent Partial Pressure [ppm]',
            ...     metric='Short circuit current density, Jsc [mA/cm2]'
            ... )
            >>> print(f"r = {result.correlation:.3f}, p = {result.p_value:.4e}")
        """
        # Validate columns
        if parameter not in data.columns:
            raise ValueError(f"Parameter '{parameter}' not found in DataFrame columns")
        if metric not in data.columns:
            raise ValueError(f"Metric '{metric}' not found in DataFrame columns")

        # Clean data: remove NaN and infinite values
        df_clean = data[[parameter, metric]].copy()
        df_clean = df_clean.dropna()
        df_clean = df_clean[np.isfinite(df_clean[parameter]) & np.isfinite(df_clean[metric])]

        if len(df_clean) < min_samples:
            logger.warning(
                f"Insufficient data: {len(df_clean)} samples (minimum: {min_samples})"
            )
            # Return empty result
            return CorrelationResult(
                parameter=parameter,
                metric=metric,
                correlation=0.0,
                p_value=1.0,
                r_squared=0.0,
                slope=0.0,
                intercept=0.0,
                std_err=0.0,
                significance="ns",
                n_samples=len(df_clean),
                equation="Insufficient data"
            )

        # Extract arrays
        x = df_clean[parameter].values
        y = df_clean[metric].values

        # Pearson correlation
        correlation, p_value = stats.pearsonr(x, y)

        # Linear regression
        slope, intercept, r_value, p_value_reg, std_err = stats.linregress(x, y)
        r_squared = r_value ** 2

        # Determine significance level
        if p_value < 0.001:
            significance = "***"
        elif p_value < 0.01:
            significance = "**"
        elif p_value < 0.05:
            significance = "*"
        else:
            significance = "ns"

        # Format equation
        sign = "+" if intercept >= 0 else "-"
        equation = f"y = {slope:.4f}x {sign} {abs(intercept):.4f} (R² = {r_squared:.4f})"

        logger.info(
            f"Correlation: {parameter} vs {metric}: "
            f"r = {correlation:.4f}, p = {p_value:.4e} ({significance})"
        )

        return CorrelationResult(
            parameter=parameter,
            metric=metric,
            correlation=correlation,
            p_value=p_value,
            r_squared=r_squared,
            slope=slope,
            intercept=intercept,
            std_err=std_err,
            significance=significance,
            n_samples=len(df_clean),
            equation=equation,
            clean_data=df_clean
        )

    def shap_analysis(
        self,
        data: pd.DataFrame,
        features: List[str],
        target: str,
        model_type: str = "RandomForest",
        n_estimators: int = 100,
        test_size: float = 0.2
    ) -> SHAPResult:
        """
        Perform SHAP feature importance analysis.

        Trains a surrogate model and uses SHAP to explain which features
        most influence the target metric.

        Args:
            data: DataFrame with experimental data
            features: List of feature column names
            target: Target column name (e.g., 'Jsc')
            model_type: "RandomForest" or "XGBoost"
            n_estimators: Number of trees
            test_size: Fraction of data for testing

        Returns:
            SHAPResult with feature importance and SHAP values

        Example:
            >>> result = analyzer.shap_analysis(
            ...     data=df,
            ...     features=['Pressure', 'Temperature', 'Time'],
            ...     target='Jsc'
            ... )
            >>> print("Feature importance:")
            >>> for feat, imp in result.feature_importance.items():
            ...     print(f"  {feat}: {imp:.4f}")
        """
        try:
            import shap
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import r2_score

            # Validate columns
            for col in features:
                if col not in data.columns:
                    raise ValueError(f"Feature '{col}' not found in DataFrame")
            if target not in data.columns:
                raise ValueError(f"Target '{target}' not found in DataFrame")

            # Clean data
            df_clean = data[features + [target]].dropna()

            if len(df_clean) < 20:
                raise ValueError(f"Insufficient data: {len(df_clean)} samples (minimum: 20)")

            X = df_clean[features].values
            y = df_clean[target].values

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Train model
            if model_type == "XGBoost":
                try:
                    from xgboost import XGBRegressor
                    model = XGBRegressor(n_estimators=n_estimators, random_state=42)
                except ImportError:
                    logger.warning("XGBoost not available, falling back to RandomForest")
                    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
                    model_type = "RandomForest"
            else:
                model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)

            model.fit(X_train, y_train)

            # Evaluate model
            y_pred = model.predict(X_test)
            r_squared = r2_score(y_test, y_pred)

            # SHAP analysis
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_train)

            # Calculate feature importance (mean absolute SHAP value)
            mean_abs_shap = np.abs(shap_values).mean(axis=0)
            feature_importance = {
                feat: float(imp) for feat, imp in zip(features, mean_abs_shap)
            }

            # Sort features by importance
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            top_features = [feat for feat, _ in sorted_features[:5]]

            logger.info(
                f"SHAP analysis complete: model R² = {r_squared:.4f}, "
                f"top feature = {top_features[0]}"
            )

            return SHAPResult(
                feature_importance=feature_importance,
                shap_values=shap_values,
                model_r_squared=r_squared,
                model_type=model_type,
                n_features=len(features),
                n_samples=len(df_clean),
                top_features=top_features
            )

        except ImportError as e:
            logger.error(f"Required package not available: {e}")
            logger.error("Install with: pip install shap scikit-learn")
            raise

    def parameter_space_optimization(
        self,
        data: pd.DataFrame,
        parameters: List[str],
        objective: str,
        maximize: bool = True,
        model_type: str = "RandomForest",
        n_estimators: int = 100
    ) -> OptimizationResult:
        """
        Optimize parameters to maximize/minimize objective metric.

        Uses surrogate modeling + global optimization (differential evolution).

        Args:
            data: DataFrame with experimental data
            parameters: List of parameter column names to optimize
            objective: Objective column name to optimize
            maximize: If True, maximize objective; if False, minimize
            model_type: "RandomForest" or "XGBoost"
            n_estimators: Number of trees

        Returns:
            OptimizationResult with optimal parameters and predicted value

        Example:
            >>> result = analyzer.parameter_space_optimization(
            ...     data=df,
            ...     parameters=['Pressure', 'Temperature'],
            ...     objective='Jsc',
            ...     maximize=True
            ... )
            >>> print(f"Optimal: {result.optimal_parameters}")
            >>> print(f"Predicted Jsc: {result.predicted_value:.2f}")
        """
        try:
            from sklearn.ensemble import RandomForestRegressor

            # Validate columns
            for col in parameters:
                if col not in data.columns:
                    raise ValueError(f"Parameter '{col}' not found in DataFrame")
            if objective not in data.columns:
                raise ValueError(f"Objective '{objective}' not found in DataFrame")

            # Clean data
            df_clean = data[parameters + [objective]].dropna()

            if len(df_clean) < 20:
                raise ValueError(f"Insufficient data: {len(df_clean)} samples (minimum: 20)")

            X = df_clean[parameters].values
            y = df_clean[objective].values

            # Train surrogate model
            if model_type == "XGBoost":
                try:
                    from xgboost import XGBRegressor
                    model = XGBRegressor(n_estimators=n_estimators, random_state=42)
                except ImportError:
                    logger.warning("XGBoost not available, using RandomForest")
                    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
                    model_type = "RandomForest"
            else:
                model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)

            model.fit(X, y)

            # Evaluate model
            from sklearn.metrics import r2_score
            y_pred = model.predict(X)
            r_squared = r2_score(y, y_pred)

            logger.info(f"Surrogate model trained: R² = {r_squared:.4f}")

            # Define bounds (min/max from data, with 10% padding)
            bounds = []
            parameter_bounds = {}

            for param in parameters:
                min_val = df_clean[param].min()
                max_val = df_clean[param].max()
                range_val = max_val - min_val
                # Add 10% padding
                lower = min_val - 0.1 * range_val
                upper = max_val + 0.1 * range_val
                bounds.append((lower, upper))
                parameter_bounds[param] = (float(lower), float(upper))

            # Define objective function
            def objective_function(params):
                prediction = model.predict([params])[0]
                if maximize:
                    return -prediction  # Minimize negative for maximization
                else:
                    return prediction

            # Global optimization
            logger.info("Starting parameter optimization...")

            result = differential_evolution(
                objective_function,
                bounds,
                seed=42,
                maxiter=1000,
                atol=1e-7,
                tol=1e-7
            )

            # Extract results
            optimal_params_dict = {
                param: float(val) for param, val in zip(parameters, result.x)
            }

            predicted_value = float(model.predict([result.x])[0])
            optimization_success = result.success
            n_iterations = result.nit

            logger.info(
                f"Optimization complete: "
                f"{'success' if optimization_success else 'failed'} "
                f"after {n_iterations} iterations"
            )

            logger.info(f"Optimal parameters: {optimal_params_dict}")
            logger.info(f"Predicted {objective}: {predicted_value:.4f}")

            return OptimizationResult(
                optimal_parameters=optimal_params_dict,
                predicted_value=predicted_value,
                optimization_success=optimization_success,
                n_iterations=n_iterations,
                convergence_message=result.message,
                parameter_bounds=parameter_bounds,
                model_r_squared=r_squared
            )

        except ImportError as e:
            logger.error(f"Required package not available: {e}")
            logger.error("Install with: pip install scikit-learn")
            raise

    def design_of_experiments(
        self,
        parameter_ranges: Dict[str, Tuple[float, float]],
        n_experiments: int,
        sampling_method: str = "LatinHypercube"
    ) -> DOEResult:
        """
        Generate optimal experimental design using statistical sampling.

        Args:
            parameter_ranges: Dict of parameter_name -> (min, max)
            n_experiments: Number of experiments to design
            sampling_method: "LatinHypercube" or "Random"

        Returns:
            DOEResult with experiment design DataFrame

        Example:
            >>> result = analyzer.design_of_experiments(
            ...     parameter_ranges={
            ...         'Pressure': (0, 100),
            ...         'Temperature': (20, 80),
            ...         'Time': (5, 60)
            ...     },
            ...     n_experiments=50
            ... )
            >>> print(result.experiment_design)
        """
        try:
            from scipy.stats import qmc

            parameters = list(parameter_ranges.keys())
            n_parameters = len(parameters)

            if n_parameters == 0:
                raise ValueError("No parameters provided")

            # Extract bounds
            lower_bounds = np.array([bounds[0] for bounds in parameter_ranges.values()])
            upper_bounds = np.array([bounds[1] for bounds in parameter_ranges.values()])

            # Sample
            if sampling_method == "LatinHypercube":
                sampler = qmc.LatinHypercube(d=n_parameters, seed=42)
                sample = sampler.random(n=n_experiments)
            elif sampling_method == "Random":
                np.random.seed(42)
                sample = np.random.random((n_experiments, n_parameters))
            else:
                raise ValueError(f"Unknown sampling method: {sampling_method}")

            # Scale to parameter ranges
            scaled_sample = qmc.scale(sample, lower_bounds, upper_bounds)

            # Create DataFrame
            experiment_design = pd.DataFrame(
                scaled_sample,
                columns=parameters
            )

            logger.info(
                f"Generated {n_experiments} experiments using {sampling_method} sampling"
            )

            return DOEResult(
                experiment_design=experiment_design,
                n_experiments=n_experiments,
                n_parameters=n_parameters,
                sampling_method=sampling_method,
                parameter_ranges=parameter_ranges
            )

        except ImportError as e:
            logger.error(f"Required package not available: {e}")
            logger.error("Install with: pip install scipy")
            raise
