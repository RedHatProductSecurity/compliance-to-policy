# -*- mode:python; coding:utf-8 -*-

# Copyright 2024 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import pathlib
from abc import ABC, abstractmethod
from typing import Any, List, Dict

from pydantic import BaseModel

from c2p.common.oscal import is_component_type_validation
from c2p.common.utils import get_dict_safely
from c2p.framework.models.policy import (
    Policy,
    RuleSet,
    Capabilities,
    Parameter
)
from c2p.framework.models.pvp_result import PVPResult
from c2p.framework.models.raw_result import RawResult
from c2p.framework import oscal_utils

from trestle.common.list_utils import as_list
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import Model as ComponentDefinitionRoot
from trestle.core.remote.cache import FetcherFactory

PluginConfig = BaseModel


class PluginCapabilities(BaseModel):
    capabilities_by_components: Dict[str, List[Capabilities]]


class PluginSpec(ABC):

    @abstractmethod
    def generate_pvp_result(self, raw_result: RawResult) -> PVPResult:
        pass

    @abstractmethod
    def generate_pvp_policy(self, policy: Policy) -> Any:
        pass


# Prototype Spec Below
class GeneratorPluginSpec(ABC):
    """Generate declarative policy or configures imperative policy scanners."""

    @abstractmethod
    def generate_pvp_policy(self, policy: Policy) -> Any:
        pass


class CollectorPluginSpec(ABC):
    """Executes, collects, and aggregates policy results."""
    @abstractmethod
    @property
    def capabilities(self) -> PluginCapabilities:
        pass

    @abstractmethod
    def set_rule_subset(self, rule_sets: List[RuleSet]) -> None:
        pass

    @abstractmethod
    def generate_pvp_result(self, raw_result: RawResult) -> PVPResult:
        pass


class PluginCapabilitiesManager():
    """
    Get available rules, covered components, and parameters.

    Notes:
    This is what the plugin is capable of running and
    assessment plans can execute based on a subset of this.

    """
    def __init__(self, pvp_name: str, capabilities_file_path: str, trestle_root: pathlib.Path) -> None:
        self._pvp_name = pvp_name
        self.capabilities: Dict[str, List[Capabilities]] = {}
        self.capabilities_path: pathlib.Path = pathlib.Path(capabilities_file_path)
        self._trestle_root = trestle_root

    def get_capabilities(self) -> PluginCapabilities:
        return PluginCapabilities(capabilities_by_components=self._read())

    def _read(self) -> Dict[str, List[Capabilities]]:
        with open(self.capabilities_path) as f:
            return json.load(f)

    def save(self) -> None:
        """Save to file."""
        with open(self.capabilities_path) as f:
            json.dump(self.capabilities, f)

    def set_capabilities(self, validation_component_definition: str) -> None:
        """Get registered components and rule/parameter sets."""
        cdef: ComponentDefinition = ComponentDefinition.oscal_read(pathlib.Path(validation_component_definition))
        compdef_root = ComponentDefinitionRoot(component_definition=cdef)

        # This is a hack, for prototyping only
        linked_component_href = cdef.import_component_definitions[0]

        rule_props_by_remarks: List[Dict[str, str]] = []
        for comp in as_list(compdef_root.component_definition.components):
            if is_component_type_validation(comp.type) and self._pvp_name in comp.title:
                rule_props_by_remarks = oscal_utils.group_props_by_remarks(comp)
                linked_comp_name = oscal_utils.get_link_component_info(comp, cdef)
                self._resolve_linked_components(linked_component_href, linked_comp_name, rule_props_by_remarks)

    def _resolve_linked_components(
            self,
            linked_component_href: str,
            link_component_name: str,
            rule_props_by_remarks: List[Dict[str, str]]
    ) -> None:
        """This is where you verify the rules exist and get the parameters"""
        import_comp: ComponentDefinition
        fetcher = FetcherFactory.get_fetcher(self._trestle_root, linked_component_href)
        import_comp, _ = fetcher.get_oscal()
        import_rule_props_by_remarks: List[Dict[str, str]] = []
        for comp in as_list(import_comp.components):
            if not is_component_type_validation(comp.type) and comp.title is link_component_name:
                import_rule_props_by_remarks = oscal_utils.group_props_by_remarks(comp)

        props_by_rule_id: Dict[str, Dict[str, str]] = {}
        for import_rule_props in import_rule_props_by_remarks:
            rule_id = get_dict_safely(import_rule_props, 'Rule_Id')
            props_by_rule_id[rule_id] = import_rule_props

        self.capabilities[link_component_name] = self._get_rulesets(rule_props_by_remarks, props_by_rule_id)

    def _get_rulesets(
            self,
            validation_rule_props_by_remarks: List[Dict[str, str]],
            props_by_rule_id: Dict[str, Dict[str, str]]
    ) -> List[Capabilities]:
        capabilities: List[Dict[str, str]] = []
        for rule_props in validation_rule_props_by_remarks:
            # get rule from main component and find params
            rule_id = get_dict_safely(rule_props, 'Rule_Id')
            import_props = props_by_rule_id.get(rule_id, {})
            capabilities.append(import_props)

        def _conv(x: Dict[str, str]) -> Capabilities:
            return Capabilities(
                rule_id=get_dict_safely(x, 'Rule_Id'),
                rule_description=get_dict_safely(x, 'Rule_Description'),
                parameter=Parameter(
                    id=get_dict_safely(x, 'Parameter_Id'),
                    description=get_dict_safely(x, 'Parameter_Description'),
                    value=get_dict_safely(x, 'Parameter_Value_Alternatives')
                )
            )

        return list(map(_conv, filter(lambda x: 'Rule_Id' in x, capabilities)))
