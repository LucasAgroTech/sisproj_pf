import sqlite3
from typing import List, Dict, Any, Optional


class CusteioManager:
    """
    Manager class for handling custeio-related database operations.
    Provides methods for filtering and retrieving hierarchical data.
    """
    
    def __init__(self, db_path: str = "sisproj_pf.db"):
        """Initialize the CusteioManager with database path."""
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_distinct_values(self, column: str, filters: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Get distinct values from a specific column, optionally filtered.
        
        Args:
            column: The column name to get distinct values from
            filters: Dictionary of column-value pairs to filter by
            
        Returns:
            List of distinct values, excluding empty/null values
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Base query
            query = f"SELECT DISTINCT {column} FROM custeio WHERE {column} IS NOT NULL AND {column} != ''"
            params = []
            
            # Add filters
            if filters:
                filter_conditions = []
                for filter_column, filter_value in filters.items():
                    if filter_value:  # Only add non-empty filters
                        filter_conditions.append(f"{filter_column} = ?")
                        params.append(filter_value)
                
                if filter_conditions:
                    query += " AND " + " AND ".join(filter_conditions)
            
            query += f" ORDER BY {column}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [row[0] for row in results]
            
        finally:
            conn.close()
    
    def filter_by_selection(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Filter custeio data based on the provided filters.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            List of dictionaries containing the filtered data
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Base query
            query = "SELECT * FROM custeio WHERE 1=1"
            params = []
            
            # Add filters
            for column, value in filters.items():
                if value:  # Only add non-empty filters
                    query += f" AND {column} = ?"
                    params.append(value)
            
            query += " ORDER BY instituicao_parceira, cod_projeto, cod_ta, resultado"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert to list of dictionaries
            return [dict(zip(column_names, row)) for row in results]
            
        finally:
            conn.close()
    
    def get_hierarchical_options(self) -> Dict[str, List[str]]:
        """
        Get all hierarchical data for populating UI components.
        
        Returns:
            Dictionary with field names as keys and lists of distinct values as values
        """
        return {
            'instituicao_parceira': self.get_distinct_values('instituicao_parceira'),
            'cod_projeto': self.get_distinct_values('cod_projeto'),
            'cod_ta': self.get_distinct_values('cod_ta'),
            'resultado': self.get_distinct_values('resultado'),
            'subprojeto': self.get_distinct_values('subprojeto')
        }
    
    def get_projects_by_institution(self, institution: str) -> List[str]:
        """Get projects filtered by institution."""
        return self.get_distinct_values('cod_projeto', {'instituicao_parceira': institution})
    
    def get_tas_by_filters(self, institution: Optional[str] = None, 
                          project: Optional[str] = None) -> List[str]:
        """Get TAs filtered by institution and/or project."""
        filters = {}
        if institution:
            filters['instituicao_parceira'] = institution
        if project:
            filters['cod_projeto'] = project
        
        return self.get_distinct_values('cod_ta', filters if filters else None)
    
    def get_results_by_filters(self, institution: Optional[str] = None,
                              project: Optional[str] = None,
                              ta: Optional[str] = None) -> List[str]:
        """Get results filtered by institution, project, and/or TA."""
        filters = {}
        if institution:
            filters['instituicao_parceira'] = institution
        if project:
            filters['cod_projeto'] = project
        if ta:
            filters['cod_ta'] = ta
        
        return self.get_distinct_values('resultado', filters if filters else None)
    
    def get_subprojects_by_filters(self, institution: Optional[str] = None,
                                  project: Optional[str] = None,
                                  ta: Optional[str] = None,
                                  result: Optional[str] = None) -> List[str]:
        """Get subprojects filtered by institution, project, TA, and/or result."""
        filters = {}
        if institution:
            filters['instituicao_parceira'] = institution
        if project:
            filters['cod_projeto'] = project
        if ta:
            filters['cod_ta'] = ta
        if result:
            filters['resultado'] = result
        
        return self.get_distinct_values('subprojeto', filters if filters else None)
    
    def test_connection(self) -> bool:
        """Test database connection and table existence."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM custeio")
            count = cursor.fetchone()[0]
            conn.close()
            return True
        except Exception as e:
            print(f"Erro na conexão com o banco: {e}")
            return False 