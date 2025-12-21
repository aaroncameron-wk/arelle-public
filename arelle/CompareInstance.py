"""
See COPYRIGHT.md for copyright information.
"""

from arelle.ModelDtsObject import ModelResource
from arelle.ModelInstanceObject import ModelFact
from arelle.ModelRelationshipSet import ModelRelationshipSet
from arelle.ModelXbrl import ModelXbrl, load
from arelle.PluginManager import pluginClassMethods
from arelle.XmlUtil import collapseWhitespace
from arelle.typing import TypeGetText

_: TypeGetText


def _factFootnotes(fact, footnotesRelSet):
    footnotes = {}
    footnoteRels = footnotesRelSet.fromModelObject(fact)
    if footnoteRels:
        # most process rels in same order between two instances, use labels to sort
        for i, footnoteRel in enumerate(sorted(footnoteRels,
                                               key=lambda r: (r.fromLabel,r.toLabel))):
            modelObject = footnoteRel.toModelObject
            if isinstance(modelObject, ModelResource):
                xml = collapseWhitespace(modelObject.viewText().strip())
                footnotes["Footnote {}".format(i+1)] = xml #re.sub(r'\s+', ' ', collapseWhitespace(modelObject.stringValue))
            elif isinstance(modelObject, ModelFact):
                footnotes["Footnoted fact {}".format(i+1)] = \
                    "{} context: {} value: {}".format(
                        modelObject.qname,
                        modelObject.contextID,
                        collapseWhitespace(modelObject.value))
    return footnotes


def _compareInstance(modelXbrl: ModelXbrl, expectedInstance: ModelXbrl, targetInstance: ModelXbrl, errMsgPrefix):
    if expectedInstance.modelDocument is None:
        modelXbrl.error("{}:expectedResultNotLoaded".format(errMsgPrefix),
                        _("Testcase expected result instance not loaded: %(file)s"),
                        modelXbrl=modelXbrl,
                        file=modelXbrl.uri,
                        messageCodes=("formula:expectedResultNotLoaded","ix:expectedResultNotLoaded"))
        return
    for pluginXbrlMethod in pluginClassMethods("CompareInstance.Loaded"):
        pluginXbrlMethod(expectedInstance, targetInstance)
    if len(expectedInstance.facts) != len(targetInstance.facts):
        targetInstance.error("{}:resultFactCounts".format(errMsgPrefix),
                                    _("Found %(countFacts)s facts, expected %(expectedFacts)s facts"),
                                    modelXbrl=modelXbrl, countFacts=len(targetInstance.facts),
                                    expectedFacts=len(expectedInstance.facts),
                                    messageCodes=("formula:resultFactCounts","ix:resultFactCounts"))
        return
    compareFootnotesRelSet = ModelRelationshipSet(targetInstance, "XBRL-footnotes")
    expectedFootnotesRelSet = ModelRelationshipSet(expectedInstance, "XBRL-footnotes")
    _matchExpectedResultIDs = not modelXbrl.hasFormulae # formula restuls have inconsistent IDs
    for expectedInstanceFact in expectedInstance.facts:
        unmatchedFactsStack = []
        compareFact = targetInstance.matchFact(expectedInstanceFact, unmatchedFactsStack, deemP0inf=True, matchId=_matchExpectedResultIDs, matchLang=False)
        if compareFact is None:
            if unmatchedFactsStack: # get missing nested tuple fact, if possible
                missingFact = unmatchedFactsStack[-1]
            else:
                missingFact = expectedInstanceFact
            # is it possible to show value mismatches?
            expectedFacts = targetInstance.factsByQname.get(missingFact.qname)
            if expectedFacts and len(expectedFacts) == 1:
                targetInstance.error("{}:expectedFactMissing".format(errMsgPrefix),
                                            _("Output missing expected fact %(fact)s, extracted value \"%(value1)s\", expected value  \"%(value2)s\""),
                                            modelXbrl=missingFact, fact=missingFact.qname, value1=missingFact.xValue, value2=next(iter(expectedFacts)).xValue,
                                            messageCodes=("formula:expectedFactMissing","ix:expectedFactMissing"))
            else:
                targetInstance.error("{}:expectedFactMissing".format(errMsgPrefix),
                                            _("Output missing expected fact %(fact)s"),
                                            modelXbrl=missingFact, fact=missingFact.qname,
                                            messageCodes=("formula:expectedFactMissing","ix:expectedFactMissing"))
        else: # compare footnotes
            expectedInstanceFactFootnotes = _factFootnotes(expectedInstanceFact, expectedFootnotesRelSet)
            compareFactFootnotes = _factFootnotes(compareFact, compareFootnotesRelSet)
            if (len(expectedInstanceFactFootnotes) != len(compareFactFootnotes) or
                    set(expectedInstanceFactFootnotes.values()) != set(compareFactFootnotes.values())):
                targetInstance.error("{}:expectedFactFootnoteDifference".format(errMsgPrefix),
                                            _("Output expected fact %(fact)s expected footnotes %(footnotes1)s produced footnotes %(footnotes2)s"),
                                            modelXbrl=(compareFact,expectedInstanceFact), fact=expectedInstanceFact.qname, footnotes1=sorted(expectedInstanceFactFootnotes.items()), footnotes2=sorted(compareFactFootnotes.items()),
                                            messageCodes=("formula:expectedFactFootnoteDifference","ix:expectedFactFootnoteDifference"))


def compareInstance(modelXbrl: ModelXbrl, targetInstance: ModelXbrl, instanceUri: str, errorCaptureLevel, errMsgPrefix) -> list[str | None]:
    expectedInstance = load(modelXbrl.modelManager,
                                      instanceUri,
                                      _("loading expected result XBRL instance"),
                                      errorCaptureLevel=errorCaptureLevel)
    _compareInstance(modelXbrl, expectedInstance, targetInstance, errMsgPrefix)
    expectedInstance.close()
    errors = targetInstance.errors
    return errors
