"""
Materials Science Domain API Clients

Provides access to materials science databases and repositories:
- Materials Project: Computed material properties database
- NOMAD: Materials data repository (experimental & computational)
- AFLOW: Automatic FLOW for Materials Discovery
- Citrination: Materials informatics platform
- PerovskiteDB: Perovskite solar cell experimental data

Example usage:
    # Materials Project
    mp = MaterialsProjectClient(api_key='your_key')
    material = mp.get_material(material_id='mp-149')

    # NOMAD repository
    nomad = NOMADClient()
    entries = nomad.search_materials(formula='TiO2')

    # AFLOW database
    aflow = AflowClient()
    material = aflow.get_material(auid='aflow:123abc')

    # Perovskite data
    perovskite = PerovskiteDBClient()
    data = perovskite.load_dataset('Summary table analysis.xlsx')
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import pandas as pd

logger = logging.getLogger(__name__)


# Data models for API responses

@dataclass
class MaterialProperties:
    """Material properties from Materials Project."""
    material_id: str
    formula: str
    structure: Optional[Dict[str, Any]] = None
    energy_per_atom: Optional[float] = None  # eV/atom
    band_gap: Optional[float] = None  # eV
    density: Optional[float] = None  # g/cm³
    formation_energy: Optional[float] = None  # eV/atom
    is_stable: Optional[bool] = None
    elasticity: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NomadEntry:
    """NOMAD repository entry."""
    entry_id: str
    upload_id: str
    material_name: Optional[str] = None
    formula: Optional[str] = None
    data_type: str = "calculation"  # "calculation" or "experiment"
    properties: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    url: Optional[str] = None


@dataclass
class AflowMaterial:
    """AFLOW material data."""
    auid: str  # AFLOW unique ID
    compound: str
    prototype: Optional[str] = None
    space_group: Optional[int] = None
    energy_per_atom: Optional[float] = None  # eV/atom
    band_gap: Optional[float] = None  # eV
    density: Optional[float] = None  # g/cm³
    properties: Optional[Dict[str, Any]] = None


@dataclass
class CitrinationData:
    """Citrination materials informatics data."""
    dataset_id: str
    material_name: str
    properties: Dict[str, float]
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PerovskiteExperiment:
    """Perovskite solar cell experimental data."""
    experiment_id: str
    composition: Dict[str, float]
    fabrication_params: Dict[str, float]
    jsc: Optional[float] = None  # Short-circuit current density (mA/cm²)
    voc: Optional[float] = None  # Open-circuit voltage (V)
    fill_factor: Optional[float] = None
    efficiency: Optional[float] = None  # Power conversion efficiency (%)
    metadata: Optional[Dict[str, Any]] = None


# API Clients

class MaterialsProjectClient:
    """
    Client for Materials Project API.

    Materials Project is the largest computed materials properties database:
    - 140,000+ materials
    - DFT-computed properties
    - Crystal structures, band gaps, formation energies

    Requires API key from https://materialsproject.org/api
    """

    BASE_URL = "https://api.materialsproject.org"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize Materials Project client.

        Args:
            api_key: Materials Project API key (get from website)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout

        if api_key:
            self.client = httpx.Client(
                timeout=timeout,
                headers={"X-API-KEY": api_key}
            )
        else:
            self.client = httpx.Client(timeout=timeout)
            logger.warning("MaterialsProjectClient initialized without API key. Limited access.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_material(self, material_id: str) -> Optional[MaterialProperties]:
        """
        Get material properties by Materials Project ID.

        Args:
            material_id: Materials Project ID (e.g., 'mp-149' for Si)

        Returns:
            MaterialProperties or None if not found
        """
        try:
            url = f"{self.BASE_URL}/materials/{material_id}/doc"
            response = self.client.get(url)
            response.raise_for_status()

            data = response.json()

            # Extract properties from response
            return MaterialProperties(
                material_id=material_id,
                formula=data.get('formula_pretty', data.get('formula', '')),
                structure=data.get('structure'),
                energy_per_atom=data.get('energy_per_atom'),
                band_gap=data.get('band_gap'),
                density=data.get('density'),
                formation_energy=data.get('formation_energy_per_atom'),
                is_stable=data.get('is_stable'),
                elasticity=data.get('elasticity'),
                metadata=data
            )

        except httpx.HTTPError as e:
            logger.error(f"Materials Project API error for {material_id}: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def search_materials(
        self,
        formula: Optional[str] = None,
        elements: Optional[List[str]] = None,
        band_gap_min: Optional[float] = None,
        band_gap_max: Optional[float] = None,
        limit: int = 100
    ) -> List[MaterialProperties]:
        """
        Search materials by criteria.

        Args:
            formula: Chemical formula (e.g., 'Fe2O3')
            elements: List of element symbols (e.g., ['Fe', 'O'])
            band_gap_min: Minimum band gap (eV)
            band_gap_max: Maximum band gap (eV)
            limit: Maximum number of results

        Returns:
            List of MaterialProperties
        """
        try:
            # Build query parameters
            params = {"limit": limit}

            if formula:
                params["formula"] = formula
            if elements:
                params["elements"] = ",".join(elements)
            if band_gap_min is not None:
                params["band_gap_min"] = band_gap_min
            if band_gap_max is not None:
                params["band_gap_max"] = band_gap_max

            url = f"{self.BASE_URL}/materials"
            response = self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            materials = []

            for item in data.get('data', []):
                materials.append(MaterialProperties(
                    material_id=item.get('material_id', ''),
                    formula=item.get('formula_pretty', ''),
                    structure=item.get('structure'),
                    energy_per_atom=item.get('energy_per_atom'),
                    band_gap=item.get('band_gap'),
                    density=item.get('density'),
                    formation_energy=item.get('formation_energy_per_atom'),
                    is_stable=item.get('is_stable'),
                    metadata=item
                ))

            return materials

        except httpx.HTTPError as e:
            logger.error(f"Materials Project search error: {e}")
            return []

    def close(self):
        """Close the HTTP client."""
        self.client.close()


class NOMADClient:
    """
    Client for NOMAD (Novel Materials Discovery) Laboratory API.

    NOMAD is a materials data repository containing:
    - Experimental data
    - Computational results
    - Published materials science data

    Public API, no authentication required.
    """

    BASE_URL = "https://nomad-lab.eu/prod/v1/api/v1"

    def __init__(self, timeout: float = 30.0):
        """Initialize NOMAD client."""
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def search_materials(
        self,
        formula: Optional[str] = None,
        elements: Optional[List[str]] = None,
        data_type: Optional[str] = None,
        limit: int = 100
    ) -> List[NomadEntry]:
        """
        Search NOMAD repository.

        Args:
            formula: Chemical formula
            elements: List of elements
            data_type: 'calculation' or 'experiment'
            limit: Maximum number of results

        Returns:
            List of NomadEntry objects
        """
        try:
            # Build query
            query = {}
            if formula:
                query["formula"] = formula
            if elements:
                query["elements"] = elements
            if data_type:
                query["entry_type"] = data_type

            url = f"{self.BASE_URL}/entries"
            response = self.client.post(
                url,
                json={
                    "query": query,
                    "pagination": {"page_size": limit}
                }
            )
            response.raise_for_status()

            data = response.json()
            entries = []

            for item in data.get('data', []):
                entries.append(NomadEntry(
                    entry_id=item.get('entry_id', ''),
                    upload_id=item.get('upload_id', ''),
                    material_name=item.get('material', {}).get('material_name'),
                    formula=item.get('material', {}).get('chemical_formula_hill'),
                    data_type=item.get('entry_type', 'calculation'),
                    properties=item.get('properties', {}),
                    metadata=item,
                    url=f"https://nomad-lab.eu/prod/v1/gui/search/entries/entry/id/{item.get('entry_id', '')}"
                ))

            return entries

        except httpx.HTTPError as e:
            logger.error(f"NOMAD API error: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_entry(self, entry_id: str) -> Optional[NomadEntry]:
        """
        Get specific NOMAD entry by ID.

        Args:
            entry_id: NOMAD entry ID

        Returns:
            NomadEntry or None if not found
        """
        try:
            url = f"{self.BASE_URL}/entries/{entry_id}"
            response = self.client.get(url)
            response.raise_for_status()

            data = response.json()

            return NomadEntry(
                entry_id=entry_id,
                upload_id=data.get('upload_id', ''),
                material_name=data.get('material', {}).get('material_name'),
                formula=data.get('material', {}).get('chemical_formula_hill'),
                data_type=data.get('entry_type', 'calculation'),
                properties=data.get('properties', {}),
                metadata=data,
                url=f"https://nomad-lab.eu/prod/v1/gui/search/entries/entry/id/{entry_id}"
            )

        except httpx.HTTPError as e:
            logger.error(f"NOMAD API error for entry {entry_id}: {e}")
            return None

    def close(self):
        """Close the HTTP client."""
        self.client.close()


class AflowClient:
    """
    Client for AFLOW (Automatic FLOW for Materials Discovery) API.

    AFLOW provides DFT-calculated materials properties:
    - 3.7 million materials
    - Crystal structure prototypes
    - Computed properties

    Public API using AFLUX query language.
    """

    BASE_URL = "http://aflowlib.org/API/aflux"

    def __init__(self, timeout: float = 30.0):
        """Initialize AFLOW client."""
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_material(self, auid: str) -> Optional[AflowMaterial]:
        """
        Get material by AFLOW unique ID.

        Args:
            auid: AFLOW unique ID (e.g., 'aflow:123abc')

        Returns:
            AflowMaterial or None if not found
        """
        try:
            # AFLUX query format
            url = f"{self.BASE_URL}/?auid({auid})"
            response = self.client.get(url)
            response.raise_for_status()

            data = response.json()

            if not data:
                return None

            item = data[0] if isinstance(data, list) else data

            return AflowMaterial(
                auid=auid,
                compound=item.get('compound', ''),
                prototype=item.get('prototype'),
                space_group=item.get('spacegroup_relax'),
                energy_per_atom=item.get('energy_atom'),
                band_gap=item.get('Egap'),
                density=item.get('density'),
                properties=item
            )

        except httpx.HTTPError as e:
            logger.error(f"AFLOW API error for {auid}: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def search_materials(
        self,
        compound: Optional[str] = None,
        elements: Optional[List[str]] = None,
        prototype: Optional[str] = None,
        limit: int = 100
    ) -> List[AflowMaterial]:
        """
        Search AFLOW database.

        Args:
            compound: Chemical formula
            elements: List of elements
            prototype: Crystal structure prototype
            limit: Maximum number of results

        Returns:
            List of AflowMaterial objects
        """
        try:
            # Build AFLUX query
            queries = []

            if compound:
                queries.append(f"compound({compound})")
            if elements:
                for elem in elements:
                    queries.append(f"species({elem})")
            if prototype:
                queries.append(f"prototype({prototype})")

            if not queries:
                logger.warning("No search criteria provided")
                return []

            query_str = ",".join(queries)
            url = f"{self.BASE_URL}/?{query_str},$paging({limit})"

            response = self.client.get(url)
            response.raise_for_status()

            data = response.json()
            materials = []

            for item in data:
                materials.append(AflowMaterial(
                    auid=item.get('auid', ''),
                    compound=item.get('compound', ''),
                    prototype=item.get('prototype'),
                    space_group=item.get('spacegroup_relax'),
                    energy_per_atom=item.get('energy_atom'),
                    band_gap=item.get('Egap'),
                    density=item.get('density'),
                    properties=item
                ))

            return materials

        except httpx.HTTPError as e:
            logger.error(f"AFLOW search error: {e}")
            return []

    def close(self):
        """Close the HTTP client."""
        self.client.close()


class CitrinationClient:
    """
    Client for Citrination materials informatics platform.

    Citrination provides materials data with machine learning:
    - Experimental data
    - Materials informatics
    - Property predictions

    Requires API key (registration needed).
    """

    BASE_URL = "https://citrination.com/api"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize Citrination client.

        Args:
            api_key: Citrination API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout

        if api_key:
            self.client = httpx.Client(
                timeout=timeout,
                headers={"X-API-Key": api_key}
            )
        else:
            self.client = httpx.Client(timeout=timeout)
            logger.warning("CitrinationClient initialized without API key. Access limited.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def search_datasets(
        self,
        query: str,
        limit: int = 100
    ) -> List[CitrinationData]:
        """
        Search Citrination datasets.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of CitrinationData objects
        """
        try:
            url = f"{self.BASE_URL}/search/pif"
            response = self.client.post(
                url,
                json={
                    "query": {"simple": query},
                    "size": limit
                }
            )
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('hits', []):
                pif = item.get('_source', {})

                # Extract properties
                properties = {}
                for prop in pif.get('properties', []):
                    name = prop.get('name', '')
                    value = prop.get('scalars', [{}])[0].get('value')
                    if name and value is not None:
                        properties[name] = value

                results.append(CitrinationData(
                    dataset_id=pif.get('uid', ''),
                    material_name=pif.get('chemicalFormula', ''),
                    properties=properties,
                    conditions=pif.get('conditions'),
                    metadata=pif
                ))

            return results

        except httpx.HTTPError as e:
            logger.error(f"Citrination search error: {e}")
            return []

    def close(self):
        """Close the HTTP client."""
        self.client.close()


class PerovskiteDBClient:
    """
    Client for Perovskite Database (file-based).

    Loads perovskite solar cell experimental data from CSV/Excel files.
    Typical format includes:
    - Experimental parameters (temperature, pressure, composition)
    - Performance metrics (Jsc, Voc, fill factor, efficiency)

    Based on Figure 3 perovskite solar cell optimization pattern.
    """

    def __init__(self):
        """Initialize Perovskite DB client."""
        pass

    def load_dataset(
        self,
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load perovskite experimental data from file.

        Args:
            file_path: Path to CSV or Excel file
            sheet_name: Sheet name (for Excel files)

        Returns:
            DataFrame with experimental data
        """
        try:
            path = Path(file_path)

            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return pd.DataFrame()

            # Load based on file extension
            if path.suffix.lower() in ['.xlsx', '.xls']:
                if sheet_name:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(file_path)
            elif path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                logger.error(f"Unsupported file format: {path.suffix}")
                return pd.DataFrame()

            logger.info(f"Loaded {len(df)} experiments from {file_path}")
            return df

        except Exception as e:
            logger.error(f"Error loading perovskite data from {file_path}: {e}")
            return pd.DataFrame()

    def parse_experiments(
        self,
        df: pd.DataFrame,
        composition_cols: Optional[List[str]] = None,
        fabrication_cols: Optional[List[str]] = None,
        jsc_col: str = 'Jsc',
        voc_col: str = 'Voc',
        ff_col: str = 'Fill Factor',
        eff_col: str = 'Efficiency'
    ) -> List[PerovskiteExperiment]:
        """
        Parse DataFrame into PerovskiteExperiment objects.

        Args:
            df: DataFrame with experimental data
            composition_cols: Column names for composition
            fabrication_cols: Column names for fabrication parameters
            jsc_col: Column name for Jsc
            voc_col: Column name for Voc
            ff_col: Column name for fill factor
            eff_col: Column name for efficiency

        Returns:
            List of PerovskiteExperiment objects
        """
        experiments = []

        for idx, row in df.iterrows():
            # Extract composition
            composition = {}
            if composition_cols:
                for col in composition_cols:
                    if col in df.columns:
                        composition[col] = row[col]

            # Extract fabrication parameters
            fabrication = {}
            if fabrication_cols:
                for col in fabrication_cols:
                    if col in df.columns:
                        fabrication[col] = row[col]

            # Extract performance metrics (row is a Pandas Series, use [] indexing)
            jsc = row[jsc_col] if jsc_col in df.columns else None
            voc = row[voc_col] if voc_col in df.columns else None
            ff = row[ff_col] if ff_col in df.columns else None
            eff = row[eff_col] if eff_col in df.columns else None

            experiments.append(PerovskiteExperiment(
                experiment_id=str(idx),
                composition=composition,
                fabrication_params=fabrication,
                jsc=jsc,
                voc=voc,
                fill_factor=ff,
                efficiency=eff,
                metadata=row.to_dict()
            ))

        return experiments
