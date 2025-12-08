"""
Integration tests for h5ad and Parquet data format support.

These tests use real data files and verify end-to-end functionality.
They require the 'science' optional dependencies (anndata, pyarrow, scanpy).

Run with: pytest tests/integration/test_data_formats.py -v
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from kosmos.execution.data_analysis import DataLoader, DataAnalyzer, DataCleaner


class TestH5adRealWorld:
    """Integration tests for h5ad file support with real single-cell data."""

    @pytest.fixture(scope="class")
    def pbmc3k_dataset(self, tmp_path_factory):
        """
        Load PBMC3k dataset - a classic single-cell benchmark dataset.

        This is a real dataset of ~2,700 peripheral blood mononuclear cells.
        Uses scanpy's built-in dataset download functionality.
        """
        try:
            import scanpy as sc
        except ImportError:
            pytest.skip("scanpy not installed - required for real h5ad tests")

        # Create temp directory for dataset
        tmp_dir = tmp_path_factory.mktemp("data")

        # Download and save PBMC3k dataset
        # This is a small (~5MB) real single-cell RNA-seq dataset
        try:
            adata = sc.datasets.pbmc3k()
            h5ad_path = tmp_dir / "pbmc3k.h5ad"
            adata.write_h5ad(h5ad_path)
            return h5ad_path, adata
        except Exception as e:
            pytest.skip(f"Could not download pbmc3k dataset: {e}")

    def test_load_pbmc3k_to_dataframe(self, pbmc3k_dataset):
        """Test loading real PBMC3k dataset as DataFrame."""
        h5ad_path, original_adata = pbmc3k_dataset

        df = DataLoader.load_h5ad(h5ad_path, to_dataframe=True)

        # Verify dimensions match original
        assert len(df) == original_adata.n_obs
        # Gene columns should exist
        assert df.shape[1] >= original_adata.n_vars

    def test_load_pbmc3k_as_anndata(self, pbmc3k_dataset):
        """Test loading real PBMC3k dataset as AnnData."""
        h5ad_path, original_adata = pbmc3k_dataset

        try:
            import anndata
        except ImportError:
            pytest.skip("anndata not installed")

        adata = DataLoader.load_h5ad(h5ad_path, to_dataframe=False)

        assert isinstance(adata, anndata.AnnData)
        assert adata.n_obs == original_adata.n_obs
        assert adata.n_vars == original_adata.n_vars

    def test_pbmc3k_analysis_workflow(self, pbmc3k_dataset):
        """Test complete analysis workflow with real single-cell data."""
        h5ad_path, _ = pbmc3k_dataset

        # Load as AnnData for preprocessing
        adata = DataLoader.load_h5ad(h5ad_path, to_dataframe=False)

        # Convert to DataFrame for statistical analysis
        df = DataLoader.load_h5ad(h5ad_path, to_dataframe=True)

        # Basic sanity checks
        assert not df.empty
        assert df.shape[0] > 100  # Should have many cells

        # Test that we can compute basic statistics
        # Filter to columns with variance (single-cell data is sparse)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        # Find columns that have some variance (not all zeros or constant)
        cols_with_variance = [
            col for col in numeric_cols
            if df[col].std() > 0.01 and df[col].nunique() > 2
        ]

        if len(cols_with_variance) >= 2:
            # Compute correlation between first two variable columns
            col1, col2 = cols_with_variance[:2]
            result = DataAnalyzer.correlation_analysis(df, col1, col2)
            assert 'correlation' in result
            assert -1 <= result['correlation'] <= 1


class TestParquetRealWorld:
    """Integration tests for Parquet file support with real analytics data."""

    @pytest.fixture(scope="class")
    def large_parquet_file(self, tmp_path_factory):
        """Create a realistic large parquet file for testing."""
        try:
            import pyarrow
        except ImportError:
            pytest.skip("pyarrow not installed")

        tmp_dir = tmp_path_factory.mktemp("data")

        # Create realistic analytics dataset
        np.random.seed(42)
        n_rows = 100_000

        df = pd.DataFrame({
            'user_id': np.random.randint(1, 10000, n_rows),
            'session_id': [f'sess_{i}' for i in range(n_rows)],
            'page_views': np.random.poisson(5, n_rows),
            'duration_seconds': np.random.exponential(120, n_rows),
            'conversion': np.random.choice([True, False], n_rows, p=[0.02, 0.98]),
            'category': np.random.choice(['home', 'product', 'cart', 'checkout'], n_rows),
            'timestamp': pd.date_range('2024-01-01', periods=n_rows, freq='s'),
            'revenue': np.where(
                np.random.choice([True, False], n_rows, p=[0.02, 0.98]),
                np.random.exponential(50, n_rows),
                0
            )
        })

        parquet_path = tmp_dir / 'analytics.parquet'
        df.to_parquet(parquet_path, compression='snappy')

        return parquet_path, df

    def test_load_large_parquet(self, large_parquet_file):
        """Test loading large parquet file efficiently."""
        parquet_path, original_df = large_parquet_file

        df = DataLoader.load_parquet(parquet_path)

        assert len(df) == 100_000
        assert list(df.columns) == list(original_df.columns)

    def test_load_parquet_column_subset(self, large_parquet_file):
        """Test loading only specific columns from parquet."""
        parquet_path, _ = large_parquet_file

        # Only load specific columns - this should be fast
        df = DataLoader.load_parquet(
            parquet_path,
            columns=['user_id', 'revenue', 'conversion']
        )

        assert len(df) == 100_000
        assert list(df.columns) == ['user_id', 'revenue', 'conversion']
        # Should not have other columns
        assert 'session_id' not in df.columns

    def test_parquet_with_analysis(self, large_parquet_file):
        """Test statistical analysis on parquet data."""
        parquet_path, _ = large_parquet_file

        df = DataLoader.load_parquet(parquet_path)

        # Test t-test: compare page_views between converters and non-converters
        result = DataAnalyzer.ttest_comparison(
            df, 'conversion', 'page_views', (True, False)
        )

        assert 'p_value' in result
        assert 't_statistic' in result
        assert result['n_group1'] + result['n_group2'] == len(df)

    def test_parquet_with_correlation(self, large_parquet_file):
        """Test correlation analysis on parquet data."""
        parquet_path, _ = large_parquet_file

        df = DataLoader.load_parquet(parquet_path)

        # Test correlation between page_views and duration
        result = DataAnalyzer.correlation_analysis(df, 'page_views', 'duration_seconds')

        assert 'correlation' in result
        assert 'p_value' in result
        assert result['n_samples'] == len(df)


class TestMixedFormatWorkflow:
    """Test workflows that combine multiple data formats."""

    def test_load_and_combine_formats(self, tmp_path):
        """Test loading data from multiple formats and combining."""
        try:
            import pyarrow
            import anndata
        except ImportError:
            pytest.skip("pyarrow and anndata required")

        # Create sample data in different formats
        np.random.seed(42)

        # CSV data
        csv_data = pd.DataFrame({
            'sample_id': ['A', 'B', 'C'],
            'condition': ['control', 'treatment', 'treatment']
        })
        csv_path = tmp_path / 'metadata.csv'
        csv_data.to_csv(csv_path, index=False)

        # Parquet data
        parquet_data = pd.DataFrame({
            'sample_id': ['A', 'B', 'C'],
            'measurement': [1.5, 2.3, 2.1]
        })
        parquet_path = tmp_path / 'measurements.parquet'
        parquet_data.to_parquet(parquet_path)

        # Load both and merge
        df_csv = DataLoader.load_data(csv_path)
        df_parquet = DataLoader.load_data(parquet_path)

        # Merge on sample_id
        merged = pd.merge(df_csv, df_parquet, on='sample_id')

        assert len(merged) == 3
        assert 'condition' in merged.columns
        assert 'measurement' in merged.columns


class TestDataFormatEdgeCases:
    """Test edge cases and error handling for data formats."""

    def test_h5ad_with_dense_matrix(self, tmp_path):
        """Test h5ad with dense (not sparse) expression matrix."""
        try:
            import anndata
        except ImportError:
            pytest.skip("anndata not installed")

        # Create AnnData with dense matrix
        np.random.seed(42)
        X = np.random.randn(50, 20)  # Dense numpy array
        adata = anndata.AnnData(X=X)

        h5ad_path = tmp_path / 'dense.h5ad'
        adata.write_h5ad(h5ad_path)

        # Load and verify
        df = DataLoader.load_h5ad(h5ad_path, to_dataframe=True)

        assert df.shape == (50, 20)

    def test_h5ad_with_empty_obs(self, tmp_path):
        """Test h5ad with no cell metadata."""
        try:
            import anndata
        except ImportError:
            pytest.skip("anndata not installed")

        # Create minimal AnnData
        np.random.seed(42)
        adata = anndata.AnnData(X=np.random.randn(10, 5))

        h5ad_path = tmp_path / 'minimal.h5ad'
        adata.write_h5ad(h5ad_path)

        # Load - should work without metadata
        df = DataLoader.load_h5ad(h5ad_path, to_dataframe=True)

        assert df.shape[0] == 10

    def test_parquet_with_compression(self, tmp_path):
        """Test parquet files with different compression codecs."""
        try:
            import pyarrow
        except ImportError:
            pytest.skip("pyarrow not installed")

        df_orig = pd.DataFrame({
            'a': range(1000),
            'b': np.random.randn(1000)
        })

        # Test different compression types
        for compression in ['snappy', 'gzip', 'brotli', None]:
            try:
                parquet_path = tmp_path / f'data_{compression}.parquet'
                df_orig.to_parquet(parquet_path, compression=compression)

                df = DataLoader.load_parquet(parquet_path)

                assert len(df) == 1000
                assert list(df.columns) == ['a', 'b']
            except Exception as e:
                # Some compression codecs may not be available
                if 'codec' in str(e).lower():
                    continue
                raise

    def test_parquet_with_nested_types(self, tmp_path):
        """Test parquet with complex nested data types."""
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            pytest.skip("pyarrow not installed")

        # Create data with nested types
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'tags': [['a', 'b'], ['c'], ['d', 'e', 'f']],
            'metadata': [{'x': 1}, {'x': 2, 'y': 3}, {'z': 4}]
        })

        parquet_path = tmp_path / 'nested.parquet'
        df.to_parquet(parquet_path)

        # Load and verify
        df_loaded = DataLoader.load_parquet(parquet_path)

        assert len(df_loaded) == 3
        assert 'tags' in df_loaded.columns


class TestRealScanpyWorkflow:
    """Test realistic scanpy analysis workflow using DataLoader."""

    @pytest.fixture
    def synthetic_scrna_data(self, tmp_path):
        """Create synthetic single-cell RNA-seq data for testing."""
        try:
            import anndata
            import scipy.sparse as sp
        except ImportError:
            pytest.skip("anndata/scipy not installed")

        np.random.seed(42)

        # Simulate 500 cells, 200 genes with cluster structure
        n_cells = 500
        n_genes = 200
        n_clusters = 3

        # Assign cells to clusters
        cluster_labels = np.repeat(['cluster_0', 'cluster_1', 'cluster_2'],
                                   [200, 150, 150])

        # Create expression matrix with cluster-specific patterns
        X = np.zeros((n_cells, n_genes))
        for i, cluster in enumerate(['cluster_0', 'cluster_1', 'cluster_2']):
            mask = cluster_labels == cluster
            # Each cluster has different gene expression patterns
            X[mask, i*50:(i+1)*50] = np.random.poisson(10, (mask.sum(), 50))
            X[mask, :] += np.random.poisson(1, (mask.sum(), n_genes))

        # Create AnnData
        adata = anndata.AnnData(
            X=sp.csr_matrix(X),
            obs=pd.DataFrame({
                'cluster': cluster_labels,
                'n_counts': X.sum(axis=1),
                'batch': np.random.choice(['batch1', 'batch2'], n_cells)
            }),
            var=pd.DataFrame({
                'gene_name': [f'Gene_{i}' for i in range(n_genes)]
            })
        )

        h5ad_path = tmp_path / 'synthetic_scrna.h5ad'
        adata.write_h5ad(h5ad_path)

        return h5ad_path

    def test_differential_expression_workflow(self, synthetic_scrna_data):
        """Test loading h5ad and performing differential expression analysis."""
        # Load data
        df = DataLoader.load_h5ad(synthetic_scrna_data, to_dataframe=True)

        # Should have gene columns and metadata
        assert 'obs_cluster' in df.columns

        # Find a gene column (not starting with obs_)
        gene_cols = [c for c in df.columns if not c.startswith('obs_')]
        assert len(gene_cols) > 0

        # Compare gene expression between clusters
        gene_col = gene_cols[0]

        # Filter to two clusters for t-test
        df_subset = df[df['obs_cluster'].isin(['cluster_0', 'cluster_1'])]

        result = DataAnalyzer.ttest_comparison(
            df_subset,
            'obs_cluster',
            gene_col,
            ('cluster_0', 'cluster_1')
        )

        assert 'p_value' in result
        assert 't_statistic' in result

    def test_batch_effect_analysis(self, synthetic_scrna_data):
        """Test analysis of batch effects in single-cell data."""
        df = DataLoader.load_h5ad(synthetic_scrna_data, to_dataframe=True)

        # Should have batch column
        assert 'obs_batch' in df.columns

        # ANOVA to check for batch effects across gene expression
        gene_cols = [c for c in df.columns if not c.startswith('obs_')]

        if len(gene_cols) > 0:
            gene_col = gene_cols[0]
            result = DataAnalyzer.anova_comparison(df, 'obs_batch', gene_col)

            assert 'p_value' in result
            assert 'f_statistic' in result
