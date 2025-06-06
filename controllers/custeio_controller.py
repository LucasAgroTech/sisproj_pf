import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.custeio_utils import CusteioManager
from typing import List, Dict, Any, Optional


class CusteioController:
    """
    Controller class for handling custeio-related operations in the application.
    This controller integrates the CusteioManager with the application's UI.
    """
    
    def __init__(self):
        """Initialize the CusteioController with a CusteioManager instance."""
        self.manager = CusteioManager()
    
    def get_institutions(self) -> List[str]:
        """
        Get all available institutions.
        
        Returns:
            List of institution names
        """
        return self.manager.get_distinct_values('instituicao_parceira')
    
    def get_projects(self, institution: Optional[str] = None) -> List[str]:
        """
        Get projects, optionally filtered by institution.
        
        Args:
            institution: The institution to filter by (optional)
            
        Returns:
            List of project codes
        """
        filters = {'instituicao_parceira': institution} if institution else None
        return self.manager.get_distinct_values('cod_projeto', filters)
    
    def get_tas(self, institution: Optional[str] = None, project: Optional[str] = None) -> List[str]:
        """
        Get TAs, optionally filtered by institution and project.
        
        Args:
            institution: The institution to filter by (optional)
            project: The project to filter by (optional)
            
        Returns:
            List of TA codes
        """
        filters = {}
        if institution:
            filters['instituicao_parceira'] = institution
        if project:
            filters['cod_projeto'] = project
        
        return self.manager.get_distinct_values('cod_ta', filters if filters else None)
    
    def get_results(self, institution: Optional[str] = None, project: Optional[str] = None, 
                   ta: Optional[str] = None) -> List[str]:
        """
        Get results, optionally filtered by institution, project, and TA.
        
        Args:
            institution: The institution to filter by (optional)
            project: The project to filter by (optional)
            ta: The TA to filter by (optional)
            
        Returns:
            List of result codes
        """
        filters = {}
        if institution:
            filters['instituicao_parceira'] = institution
        if project:
            filters['cod_projeto'] = project
        if ta:
            filters['cod_ta'] = ta
        
        return self.manager.get_distinct_values('resultado', filters if filters else None)
    
    def get_subprojects(self, institution: Optional[str] = None, project: Optional[str] = None,
                       ta: Optional[str] = None, result: Optional[str] = None) -> List[str]:
        """
        Get subprojects, optionally filtered by institution, project, TA, and result.
        
        Args:
            institution: The institution to filter by (optional)
            project: The project to filter by (optional)
            ta: The TA to filter by (optional)
            result: The result to filter by (optional)
            
        Returns:
            List of subproject names
        """
        filters = {}
        if institution:
            filters['instituicao_parceira'] = institution
        if project:
            filters['cod_projeto'] = project
        if ta:
            filters['cod_ta'] = ta
        if result:
            filters['resultado'] = result
        
        return self.manager.get_distinct_values('subprojeto', filters if filters else None)
    
    def filter_custeio(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Filter custeio data based on the provided filters.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            List of dictionaries containing the filtered data
        """
        # Remove empty filters
        clean_filters = {k: v for k, v in filters.items() if v}
        return self.manager.filter_by_selection(clean_filters)
    
    def get_hierarchical_data(self) -> Dict[str, List[str]]:
        """
        Get all hierarchical data for populating UI components.
        
        Returns:
            Dictionary with field names as keys and lists of distinct values as values
        """
        return self.manager.get_hierarchical_options()


# Example of how to use the controller in a view
def example_controller_usage():
    """Demonstrate how to use the CusteioController in a view."""
    controller = CusteioController()
    
    print("Getting all institutions:")
    institutions = controller.get_institutions()
    print(institutions)
    
    if institutions:
        selected_institution = institutions[0]
        print(f"\nSelected institution: {selected_institution}")
        
        print("Getting projects for the selected institution:")
        projects = controller.get_projects(selected_institution)
        print(projects)
        
        if projects:
            selected_project = projects[0]
            print(f"\nSelected project: {selected_project}")
            
            print("Getting TAs for the selected project:")
            tas = controller.get_tas(selected_institution, selected_project)
            print(tas)
            
            # Example of filtering
            print("\nFiltering data:")
            filters = {
                'instituicao_parceira': selected_institution,
                'cod_projeto': selected_project
            }
            filtered_data = controller.filter_custeio(filters)
            print(f"Found {len(filtered_data)} records")
            
            # Display a few records
            for i, record in enumerate(filtered_data[:3]):
                print(f"Record {i+1}: {record}")


if __name__ == "__main__":
    example_controller_usage() 