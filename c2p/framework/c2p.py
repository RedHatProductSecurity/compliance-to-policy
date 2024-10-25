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

import pathlib
from typing import Dict, List, Optional, Tuple

from pydantic.v1 import BaseModel
from trestle import __version__ as TRESTLE_VERSION
from trestle.oscal import OSCAL_VERSION
from trestle.oscal.assessment_results import (
    AssessmentResults,
    ImportAp,
    Observation,
    Result,
)
from trestle.oscal.catalog import Catalog
from trestle.oscal.catalog import Model as CatalogRoot
from trestle.oscal.common import (
    Link,
    Metadata,
    Property,
    RelevantEvidence,
    SubjectReference,
)
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import Model as ComponentDefinitionRoot
from trestle.oscal.profile import Model as ProfileRoot
from trestle.oscal.profile import Profile

from c2p.common.oscal import is_component_type_validation
from c2p.common.utils import get_dict_safely
from c2p.framework import oscal_utils
from c2p.framework.models.c2p_config import C2PConfig
from c2p.framework.models.pvp_result import set_defaults
from c2p.framework.models.models_pb2 import Policy, Parameter, Rule, PVPResult, Check

RuleId = str


class _RuleSet(BaseModel):
    effective_rule_id: str
    effective_check_id: str
    rule_id: str
    rule_description: Optional[str]
    check_id: Optional[str]
    check_description: Optional[str]
    raw: Optional[Dict[str, str]]


class C2P:
    def __init__(self, c2p_config: C2PConfig):
        self._c2p_config = c2p_config
        if c2p_config.compliance.catalog:
            catalog = Catalog.oscal_read(pathlib.Path(c2p_config.compliance.catalog))
            self._catalog_root: CatalogRoot = CatalogRoot(catalog=catalog)
        if c2p_config.compliance.profile:
            profile = Profile.oscal_read(pathlib.Path(c2p_config.compliance.profile))
            self._profile_root: ProfileRoot = ProfileRoot(profile=profile)
        cdef = ComponentDefinition.oscal_read(pathlib.Path(c2p_config.compliance.component_definition))
        self._component_root: ComponentDefinitionRoot = ComponentDefinitionRoot(component_definition=cdef)
        self._params_by_rule: Dict[str, str] = {}

    def set_pvp_result(self, pvp_result: PVPResult):
        self._c2p_config.pvp_result = pvp_result

    def result_to_oscal(self) -> AssessmentResults:
        pvp_result = set_defaults(self._c2p_config.pvp_result)
        timestamp = oscal_utils.get_datetime_str()
        metadata = Metadata(
            title=self._c2p_config.result_title,
            oscal_version=OSCAL_VERSION,
            version=TRESTLE_VERSION,
            last_modified=timestamp,
        )
        import_ap = ImportAp(href='https://not-available-for-now')
        value = AssessmentResults(
            uuid=oscal_utils.uuid(),
            metadata=metadata,
            import_ap=import_ap,
            results=[self._get_result(pvp_result)],
        )
        return value

    def get_policy(self) -> Policy:
        rule_sets, params = self.get_rule_sets()
        return Policy(
            rules=rule_sets,
            parameters=params
        )

    def get_rule_sets(self) -> Tuple[List[Rule], List[Parameter]]:
        params = self.get_parameters()
        _rule_sets = self._get_rule_sets()

        parameter: Optional[Parameter] = None
        for rule in _rule_sets:
            param_id = self._params_by_rule.get(rule.effective_rule_id, "")
            parameter = Parameter(name=param_id)

        def _conv(x: _RuleSet):
            check = Check(
                name=x.effective_check_id
            )
            return Rule(
                name=x.effective_rule_id,
                description=x.rule_description,
                check=check,
                parameter=parameter
            )

        return list(map(_conv, _rule_sets)), params

    def get_parameters(self) -> List[Parameter]:
        return self._get_parameters()

    def _get_rule_sets(self) -> List[_RuleSet]:
        rule_sets: List[Dict[str, str]] = []
        for comp in self._component_root.component_definition.components:
            if is_component_type_validation(comp.type) and comp.title == self._c2p_config.pvp_name:
                rule_sets = oscal_utils.group_props_by_remarks(comp)

        def _conv(x: Dict[str, str]) -> _RuleSet:
            return _RuleSet(
                rule_id=get_dict_safely(x, 'Rule_Id'),
                rule_description=get_dict_safely(x, 'Rule_Description'),
                check_id=get_dict_safely(x, 'Check_Id'),
                check_description=get_dict_safely(x, 'Check_Description'),
                effective_rule_id=get_dict_safely(x, self._c2p_config.compliance.rule_id_column),
                effective_check_id=get_dict_safely(x, self._c2p_config.compliance.check_id_column),
                raw=x,
            )

        return list(map(_conv, filter(lambda x: 'Rule_Id' in x, rule_sets)))

    def _find_rule_set(self, rule_id: str, rule_sets: List[_RuleSet]) -> Optional[_RuleSet]:
        return next(filter(lambda x: x.effective_rule_id == rule_id, rule_sets), None)

    def _get_parameters(self) -> List[Parameter]:
        parameters: List[Dict[str, str]] = []
        for component in self._component_root.component_definition.components:
            if not is_component_type_validation(component.type):
                parameters = oscal_utils.group_props_by_remarks(component)

        def _conv(x: Dict[str, str]) -> Parameter:
            rule_id = get_dict_safely(x, 'Rule_Id')
            param_id = get_dict_safely(x, 'Parameter_Id')
            self._params_by_rule[rule_id] = param_id
            return Parameter(
                name=get_dict_safely(x, 'Parameter_Id'),
                description=get_dict_safely(x, 'Parameter_Description'),
                selected_value=get_dict_safely(x, 'Parameter_Value_Alternatives'),
            )

        return list(map(_conv, filter(lambda x: 'Parameter_Id' in x, parameters)))

    def _find_parameter(self, id: str, parameters: List[Parameter]) -> Optional[Parameter]:
        return next(filter(lambda x: x.id == id, parameters), None)

    def _get_result(self, pvp_result: PVPResult) -> Result:
        """Return result."""
        result = Result(
            uuid=oscal_utils.uuid(),
            title=self._c2p_config.result_title,
            description=self._c2p_config.result_description,
            start=oscal_utils.get_datetime_str(),
            observations=self._get_observations(pvp_result),
            reviewed_controls=oscal_utils.reviewed_controls(self._component_root.component_definition),
        )
        if pvp_result.links != None:
            result.links = list(map(lambda x: Link(href=x.href, text=x.description), pvp_result.links))
        if self._c2p_config.result_labels != None:
            result.props = list(map(lambda x: Property(name='label', value=x), self._c2p_config.result_labels))
        return result

    def _get_observations(self, pvp_result: PVPResult) -> List[Observation]:
        rule_sets = self._get_rule_sets()
        observations = []
        for observation in pvp_result.observations:
            rule_set = self._find_rule_set(observation.name, rule_sets)
            if rule_set is not None:
                subjects = []
                for subject in observation.subjects:
                    props: List[Property] = []
                    oscal_utils.add_prop(props, 'resource-id', subject.resource_id, [])
                    oscal_utils.add_prop(props, 'result', subject.result, [])
                    oscal_utils.add_prop(props, 'evaluated-on', subject.evaluated_on.ToDatetime(), [])
                    oscal_utils.add_prop(props, 'reason', subject.reason, [])
                    s = SubjectReference(
                        subject_uuid=oscal_utils.uuid(), title=subject.title, type='inventory-item', props=props
                    )
                    subjects.append(s)

                relevant_evidences = []
                if observation.evidence_refs is not None:
                    for rel in observation.evidence_refs:
                        relevant_evidences.append(RelevantEvidence(href=rel.href, description=rel.description))

                props = []
                oscal_utils.add_prop(props, 'assessment-rule-id', rule_set.effective_rule_id, [])
                method_list: List[str] = []
                for method in observation.methods:
                    method_list.append(method)
                o = Observation(
                    uuid=oscal_utils.uuid(),
                    title=observation.name,
                    description=observation.name,
                    methods=method_list,
                    props=props,
                    subjects=subjects,
                    collected=observation.collected_at.ToDatetime(),
                )
                if len(relevant_evidences) > 0:
                    o.relevant_evidence = relevant_evidences
                observations.append(o)
        return observations
