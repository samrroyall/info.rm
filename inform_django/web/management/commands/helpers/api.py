import logging
from requests import get, Response
from sys import exit
from typing import Dict, List, Union
# project imports
from . import config

# Json Type Aliases
JsonData = Union[ str, int, None ]
Json = Dict[ str, Union[JsonData, Dict[str, JsonData], List[ JsonData ]] ]

class Request:
    _url: str = config.api_url
    _host: str = config.api_host
    _host_header: str = config.api_host
    _key: str = config.api_key
    _key_header: str = config.api_key_header
    _headers: Dict[str, str] = {
        _host_header: _host,
        _key_header: _key,
    }

    def __init__(
        self, 
        endpoint: str, 
        params: Dict[str, Union[str, int]],
        log_level: int = logging.DEBUG,
    ) -> None:
        self.endpoint = endpoint
        self.params = params
        if log_level not in config.LogLevel:
            logging.warning(f"Invalid log level '{log_level}' provided to Requests class. Proceeding with default.")
        self.log_level = log_level
        logging.basicConfig(level=self.log_level)

    def api_get_request(self, page: int) -> Response:
        current_params: Dict[str, Union[str, int]] = self.params.copy()
        if page > 1:
            current_params["page"] = page
        logging.info(f"Request to '{self._url}{self.endpoint}' attempted with the following parameters: {current_params}.")
        response: Response = get(
            url=f"{self._url}{self.endpoint}", 
            headers=self._headers, 
            params=current_params,
        )
        if (response.status_code != 200):
            logging.warning(f"Request to '{self._url}{self.endpoint}' failed with status code {response.status_code}.")
            response.raise_for_status()
        logging.info(f"Request to '{self._url}{self.endpoint}?page={page}' successful.")
        return response

    def handle_call(self, max_retries: int, page: int) -> Response:
        try:
            return self.api_get_request(page)
        except:
            retries = 1
            while retries <= max_retries:
                logging.warning(f"Retrying... ({retries}/{max_retries})")
                try:
                    return self.api_get_request(page)
                except:
                    retries += 1
            logging.error(f"Request to '{self._url}{self.endpoint}' failed after {max_retries} retries.")

    def handle_pagination(self, max_retries: int) -> List[Json]:
        data_dict: Dict[int, Json] = {}
        total_pages: Union[int, None] = None
        page: int = 1
        # for each page, add paginated result to dictionary
        while (total_pages is None or page < total_pages):
            json_response: Json = self.handle_call(max_retries, page).json()
            # handle paging    
            if "paging" not in json_response:
                logging.critical(f"Response to request to '{self._url}{self.endpoint}' does not contain key `paging`.")
                exit(1)
            if "total" not in json_response.get("paging"):
                logging.critical(f"Response to request to '{self._url}{self.endpoint}' does not contain key `paging['total']`.")
                exit(1)
            # update total_pages variable
            total_pages = json_response.get("paging").get("total") if total_pages is None else total_pages
            # update data dictionary with response
            data_dict[page] = json_response
            page += 1
        # combine results into data_list
        data_list: List[Json] = []
        for results in data_dict.values():
            if "response" not in results:
                logging.critical(f"Response to request to '{self._url}{self.endpoint}' does not contain key `response`.")
                exit(1)
                
            data_list.extend(results.get("response"))
        logging.info(f"Response to request to '{self._url}{self.endpoint}' yielded {len(data_list)} results.")
        return data_list

    def request(self, max_retries: int = 5) -> List[Json]: 
        response_data: List[Json] = self.handle_pagination(max_retries)
        return response_data