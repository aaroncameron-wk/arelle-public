from pathlib import PurePath
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig

TIMING = {f'conf/{k}': v for k, v in {
    '605-instance-syntax/605-45-cover-page-facts-general-case/605-45-cover-page-facts-general-case-testcase.xml': 0.651,
    '609-linkbase-syntax/609-10-general-namespace-specific-custom-arc-restrictions/609-10-general-namespace-specific-custom-arc-restrictions-testcase.xml': 0.666,
    '614-calculation-syntax/614-03-calculation-same-period-types/614-03-calculation-same-period-types-testcase.xml': 0.745,
    '603-filing-syntax/603-10-schema-required/603-10-schema-required-testcase.xml': 0.747,
    '605-instance-syntax/605-38-forever-period/605-38-forever-period-testcase.xml': 0.775,
    '624-rendering/09-start-end-labels/gd/09-start-end-labels-gd-testcase.xml': 0.78,
    '624-rendering/04-primary-axis/gd/04-primary-axis-gd-testcase.xml': 0.793,
    '614-calculation-syntax/614-02-calculation-is-unitary/614-02-calculation-is-unitary-testcase.xml': 0.828,
    '614-calculation-syntax/614-01-calculation-order-required/614-01-calculation-order-required-testcase.xml': 0.829,
    '605-instance-syntax/605-08-no-unused-contexts/605-08-no-unused-contexts-testcase.xml': 0.846,
    '624-rendering/15-equity-changes/gw/15-equity-changes-gw-testcase.xml': 0.846,
    '605-instance-syntax/605-29-footnote-loc-role-not-custom/605-29-footnote-loc-role-not-custom-testcase.xml': 0.852,
    '624-rendering/05-fact-selection/gd/05-fact-selection-gd-testcase.xml': 0.858,
    '624-rendering/18-numeric/gd/18-numeric-gd-testcase.xml': 0.873,
    '624-rendering/03-unit-selection/gd/03-unit-selection-gd-testcase.xml': 0.892,
    '607-schema-syntax/607-32-nonnumeric-instant/607-32-nonnumeric-instant-testcase.xml': 0.912,
    '616-definition-syntax/616-01-definition-relationship-has-order/616-01-definition-relationship-has-order-testcase.xml': 0.921,
    '603-filing-syntax/603-03-filename-pattern/603-03-filename-pattern-testcase.xml': 0.923,
    '605-instance-syntax/605-01-entity-identifier-scheme/605-01-entity-identifier-scheme-testcase.xml': 0.928,
    '609-linkbase-syntax/609-04-no-missing-default-roles/609-04-no-missing-default-roles-testcase.xml': 0.929,
    '525-ix-syntax/efm/20-fraction/20-fraction-efm-testcase.xml': 0.945,
    '525-ix-syntax/efm/10-header/10-header-efm-testcase.xml': 0.965,
    '607-schema-syntax/607-21-abstracts-duration/607-21-abstracts-duration-testcase.xml': 0.968,
    '525-ix-syntax/efm/18-tuple/18-tuple-efm-testcase.xml': 0.983,
    '525-ix-syntax/efm/12-references/12-references-efm-testcase.xml': 0.986,
    '605-instance-syntax/605-22-other-dei-elements-optional/605-22-other-dei-elements-optional-testcase.xml': 0.986,
    '605-instance-syntax/605-32-footnote-loc-fragment-portable/605-32-footnote-loc-fragment-portable-testcase.xml': 0.987,
    '612-presentation-syntax/612-08-axis-requires-domain-child/612-08-axis-requires-domain-child-testcase.xml': 0.993,
    '603-filing-syntax/603-08-only-one-instance/603-08-only-one-instance-testcase.xml': 1.005,
    '605-instance-syntax/605-03-entity-identifier-all-identical/605-03-entity-identifier-all-identical-testcase.xml': 1.022,
    '612-presentation-syntax/612-01-presentation-order-required/612-01-presentation-order-required-testcase.xml': 1.023,
    '607-schema-syntax/607-19-no-ext-elt-tuples/607-19-no-ext-elt-tuples-testcase.xml': 1.026,
    '607-schema-syntax/607-01-no-include/607-01-no-include-testcase.xml': 1.034,
    '607-schema-syntax/607-28-domain-member-duration/607-28-domain-member-duration-testcase.xml': 1.039,
    '525-ix-syntax/ned/20-viewer-lang/20-viewer-testcase.xml': 1.046,
    '607-schema-syntax/607-10-role-types-no-duplicates/607-10-role-types-no-duplicates-testcase.xml': 1.046,
    '607-schema-syntax/607-25-no-custom-substitutiongroups/607-25-no-custom-substitutiongroups-testcase.xml': 1.05,
    '612-presentation-syntax/612-09-presented-units-order/612-09-presented-units-order-testcase.xml': 1.053,
    '607-schema-syntax/607-20-no-typed-domain-ref/607-20-no-typed-domain-ref-testcase.xml': 1.061,
    '605-instance-syntax/605-11-no-duplicate-units/605-11-no-duplicate-units-testcase.xml': 1.07,
    '603-filing-syntax/603-04-no-html-character-entities/603-04-no-html-character-entities-testcase.xml': 1.078,
    '605-instance-syntax/605-17-decimals-not-precision/605-17-decimals-not-precision-testcase.xml': 1.078,
    '618-reference-syntax/618-02-no-added-references/618-02-no-added-references-testcase.xml': 1.082,
    '525-ix-syntax/ned/14-baseuri/14-baseuri-ned-testcase.xml': 1.085,
    '616-definition-syntax/616-08-notall-all-are-distinct/616-08-notall-all-are-distinct-testcase.xml': 1.089,
    '624-rendering/16-qualifiers/gd/16-qualifiers-gd-testcase.xml': 1.092,
    '624-rendering/14-cash-flows/gd/14-cash-flows-gd-testcase.xml': 1.111,
    '616-definition-syntax/616-06-notall-must-have-closed-false/616-06-notall-must-have-closed-false-testcase.xml': 1.117,
    '609-linkbase-syntax/609-07-linkbases-distinct/609-07-linkbases-distinct-testcase.xml': 1.128,
    '624-rendering/21-multiple/gd/21-multiple-gd-testcase.xml': 1.128,
    '605-instance-syntax/605-39-dimensions/605-39-dimensions-testcase.xml': 1.131,
    '607-schema-syntax/607-14-arcrole-types-no-duplicates/607-14-arcrole-types-no-duplicates-testcase.xml': 1.133,
    '607-schema-syntax/607-26-lineitems-abstract/607-26-lineitems-abstract-testcase.xml': 1.134,
    '607-schema-syntax/607-31-fraction-item-type/607-31-fraction-item-type-testcase.xml': 1.134,
    '624-rendering/17-uncategorized-facts/gd/17-uncategorized-facts-gd-testcase.xml': 1.15,
    '605-instance-syntax/605-02-entity-identifier-match-cik/605-02-entity-identifier-match-cik-testcase.xml': 1.151,
    '605-instance-syntax/605-33-footnote-linked-to-facts/605-33-footnote-linked-to-facts-testcase.xml': 1.166,
    '624-rendering/02-contexts/gd/02-contexts-gd-testcase.xml': 1.17,
    '612-presentation-syntax/612-02-presentation-order-distinct/612-02-presentation-order-distinct-testcase.xml': 1.171,
    '525-ix-syntax/efm/04-nonnumeric/04-nonnumeric-efm-testcase.xml': 1.172,
    '612-presentation-syntax/612-06-presentation-single-root/612-06-presentation-single-root-testcase.xml': 1.174,
    '605-instance-syntax/605-04-no-scenario-elements/605-04-no-scenario-elements-testcase.xml': 1.203,
    '607-schema-syntax/607-17-valid-ext-elt-id/607-17-valid-ext-elt-id-testcase.xml': 1.206,
    '525-ix-syntax/efm/16-redlining/16-redlining-testcase.xml': 1.223,
    '610-label-syntax/610-05-no-documentation-replacement/610-05-no-documentation-replacement-testcase.xml': 1.234,
    '626-rendering-syntax/626-03-no-matching-durations/626-03-no-matching-durations-testcase.xml': 1.246,
    '607-schema-syntax/607-23-dimensions-named-axis/607-23-dimensions-named-axis-testcase.xml': 1.256,
    '624-rendering/22-workbook/gd/22-workbook-gd-testcase.xml': 1.265,
    '614-calculation-syntax/614-04-summation-item-undirected/614-04-summation-item-undirected-testcase.xml': 1.266,
    '605-instance-syntax/605-28-footnote-no-custom-footnote-role/605-28-footnote-no-custom-footnote-role-testcase.xml': 1.269,
    '525-ix-syntax/ned/01-format/01-format-ned-testcase.xml': 1.276,
    '624-rendering/11-row-headings/gd/11-row-headings-gd-testcase.xml': 1.286,
    '624-rendering/01-presentation-groups/gd/01-presentation-groups-gd-testcase.xml': 1.289,
    '607-schema-syntax/607-24-hypercubes-named-table/607-24-hypercubes-named-table-testcase.xml': 1.292,
    '605-instance-syntax/605-37-nonzero-truncation/605-37-nonzero-truncation-testcase.xml': 1.3,
    '616-definition-syntax/616-07-notall-axis-requires-all/616-07-notall-axis-requires-all-testcase.xml': 1.302,
    '605-instance-syntax/605-44-custom-axis/605-44-custom-axis-testcase.xml': 1.305,
    '624-rendering/10-column-headings/gd/10-column-headings-gd-testcase.xml': 1.306,
    '525-ix-syntax/ned/10-header/10-header-ned-testcase.xml': 1.328,
    '612-presentation-syntax/612-05-distinct-preferred-labels/612-05-distinct-preferred-labels-testcase.xml': 1.328,
    '616-definition-syntax/616-05-one-all-per-base-set/616-05-one-all-per-base-set-testcase.xml': 1.331,
    '609-linkbase-syntax/609-06-no-custom-arcroles/609-06-no-custom-arcroles-testcase.xml': 1.335,
    '624-rendering/20-filing-summary/gd/20-filing-summary-gd-testcase.xml': 1.337,
    '614-calculation-syntax/614-07-vip-calculation-link-validations/614-07-vip-calculation-link-validations-testcase.xml': 1.339,
    '607-schema-syntax/607-18-nillable-true/607-18-nillable-true-testcase.xml': 1.355,
    '525-ix-syntax/ned/05-exclude/05-exclude-ned-testcase.xml': 1.371,
    '610-label-syntax/610-08-label-is-trimmed/610-08-label-is-trimmed-testcase.xml': 1.399,
    '605-instance-syntax/605-07-no-duplicate-contexts/605-07-no-duplicate-contexts-testcase.xml': 1.414,
    '616-definition-syntax/616-03-dimension-domain-is-domain/616-03-dimension-domain-is-domain-testcase.xml': 1.416,
    '605-instance-syntax/605-27-footnote-no-substitutions/605-27-footnote-no-substitutions-testcase.xml': 1.43,
    '607-schema-syntax/607-15-arcrole-has-definition/607-15-arcrole-has-definition-testcase.xml': 1.434,
    '525-ix-syntax/ned/13-resources/13-resources-ned-testcase.xml': 1.444,
    '609-linkbase-syntax/609-05-no-custom-resource-roles/609-05-no-custom-resource-roles-testcase.xml': 1.48,
    '607-schema-syntax/607-30-uri-length/607-30-uri-length-testcase.xml': 1.481,
    '625-rr-rendering/02-bar-charts/gd/02-bar-charts-gd-testcase.xml': 1.497,
    '610-label-syntax/610-04-distinct-standard-labels/610-04-distinct-standard-labels-testcase.xml': 1.5,
    '605-instance-syntax/605-19-required-context/605-19-required-context-testcase.xml': 1.501,
    '525-ix-syntax/ned/15-xmllang/15-xmllang-ned-testcase.xml': 1.51,
    '605-instance-syntax/605-13-english-default/605-13-english-default-testcase.xml': 1.567,
    '607-schema-syntax/607-07-recommended-prefix-required/607-07-recommended-prefix-required-testcase.xml': 1.571,
    '607-schema-syntax/607-13-arcrole-authority-matches-namespace/607-13-arcrole-authority-matches-namespace-testcase.xml': 1.571,
    '525-ix-syntax/efm/09-footnote/09-footnote-efm-testcase.xml': 1.585,
    '622-only-supported-locations/622-05-ix-no-unsupported-locations/622-05-ix-no-unsupported-locations-testcase.xml': 1.601,
    '612-presentation-syntax/612-07-period-type-preferred-label-mismatch/612-07-period-type-preferred-label-mismatch-testcase.xml': 1.605,
    '603-filing-syntax/603-06-uri-recognized/603-06-uri-recognized-testcase.xml': 1.609,
    '603-filing-syntax/603-05-only-xml-or-numeric-character-refs/603-05-only-xml-or-numeric-character-refs-testcase.xml': 1.611,
    '607-schema-syntax/607-11-role-types-pre-cal-def/607-11-role-types-pre-cal-def-testcase.xml': 1.622,
    '618-reference-syntax/618-01-no-custom-references/618-01-no-custom-references-testcase.xml': 1.655,
    '605-instance-syntax/605-23-required-context-match-cik/605-23-required-context-match-cik-testcase.xml': 1.663,
    '607-schema-syntax/607-09-role-authority-matches-namespace/607-09-role-authority-matches-namespace-testcase.xml': 1.684,
    '605-instance-syntax/605-14-foreign-content-needs-english/605-14-foreign-content-needs-english-testcase.xml': 1.717,
    '525-ix-syntax/ned/11-hidden/11-hidden-ned-testcase.xml': 1.718,
    '610-label-syntax/610-06-no-special-chars-unless-documentation/610-06-no-special-chars-unless-documentation-testcase.xml': 1.755,
    '612-presentation-syntax/612-11-vip-presentation-link-validations/612-11-vip-presentation-link-validations-testcase.xml': 1.763,
    '616-definition-syntax/616-09-consecutive-relationship-required/616-09-consecutive-relationship-required-testcase.xml': 1.765,
    '610-label-syntax/610-02-element-used-one-label-per-role/610-02-element-used-one-label-per-role-testcase.xml': 1.815,
    '610-label-syntax/610-01-element-used-has-label/610-01-element-used-has-label-testcase.xml': 1.828,
    '603-filing-syntax/603-11-no-xml-base/603-11-no-xml-base-testcase.xml': 1.835,
    '605-instance-syntax/605-34-footnote-xhtml/605-34-footnote-xhtml-testcase.xml': 1.867,
    '624-rendering/624-23-Resource-Extraction-Payment-Rendering/624-23-Resource-Extraction-Payment-Rendering-testcase.xml': 1.878,
    '525-ix-syntax/ned/08-relationship/08-relationship-ned-testcase.xml': 1.901,
    '605-instance-syntax/605-15-text-blocks-xml-well-formed/605-15-text-blocks-xml-well-formed-testcase.xml': 1.917,
    '525-ix-syntax/ned/00-filing/00-filing-ned-testcase.xml': 1.947,
    '607-schema-syntax/607-03-ext-not-standard-namespace/607-03-ext-not-standard-namespace-testcase.xml': 1.947,
    '605-instance-syntax/605-25-no-domain-items-as-facts/605-25-no-domain-items-as-facts-testcase.xml': 1.951,
    '625-rr-rendering/01-embedding-commands/gd/01-embedding-commands-gd-testcase.xml': 1.975,
    '612-presentation-syntax/612-03-element-used-is-presented/612-03-element-used-is-presented-testcase.xml': 1.977,
    '525-ix-syntax/ned/19-multiio/19-multiio-ned-testcase.xml': 2.014,
    '607-schema-syntax/607-27-domain-member-type/607-27-domain-member-type-testcase.xml': 2.021,
    '607-schema-syntax/607-04-valid-ext-namespace-format/607-04-valid-ext-namespace-format-testcase.xml': 2.032,
    '607-schema-syntax/607-29-name-length/607-29-name-length-testcase.xml': 2.085,
    '607-schema-syntax/607-16-no-ext-name-same-as-base/607-16-no-ext-name-same-as-base-testcase.xml': 2.088,
    '525-ix-syntax/ned/02-transform/02-transform-ned-testcase.xml': 2.141,
    '605-instance-syntax/605-09-start-and-end-dates-distinct/605-09-start-and-end-dates-distinct-testcase.xml': 2.19,
    '626-rendering-syntax/626-07-empty-bar-chart/626-07-empty-bar-chart-testcase.xml': 2.269,
    '626-rendering-syntax/626-09-Primary-Axis-On-Rows/626-09-primary-axis-on-rows-testcase.xml': 2.302,
    '525-ix-syntax/efm/21-duplicates/21-duplicates-efm-testcase.xml': 2.327,
    '626-rendering-syntax/626-08-too-many-annual-return-facts/626-08-too-many-annual-return-facts-testcase.xml': 2.338,
    '610-label-syntax/610-03-foreign-label-requires-english/610-03-foreign-label-requires-english-testcase.xml': 2.352,
    '525-ix-syntax/efm/01-format/01-format-efm-testcase.xml': 2.396,
    '607-schema-syntax/607-12-role-has-definition/607-12-role-has-definition-testcase.xml': 2.507,
    '525-ix-syntax/ned/06-ids/06-ids-ned-testcase.xml': 2.508,
    '614-calculation-syntax/614-05-calculation-has-presentation-same-base-set/614-05-calculation-has-presentation-same-base-set-testcase.xml': 2.532,
    '616-definition-syntax/616-11-vip-definition-link-validations/616-11-vip-definition-link-validations-testcase.xml': 2.578,
    '626-rendering-syntax/626-06-embedding-incomplete-ordering-axes/626-06-embedding-incomplete-ordering-axes-testcase.xml': 2.599,
    '624-rendering/12-footnotes/gd/12-footnotes-gd-testcase.xml': 2.737,
    '605-instance-syntax/605-12-no-duplicate-facts/605-12-no-duplicate-facts-testcase.xml': 2.868,
    '614-calculation-syntax/614-10-RXP-calculation-link-validations/614-10-RXP-calculation-link-validations-testcase.xml': 2.926,
    '605-instance-syntax/605-36-measure-local-name/605-36-measure-local-name-testcase.xml': 2.934,
    '624-rendering/13-flow-through/gd/13-flow-through-gd-testcase.xml': 2.971,
    '609-linkbase-syntax/609-09-priority-less-than-ten/609-09-priority-less-than-ten-testcase.xml': 3.013,
    '605-instance-syntax/605-53-former-address-cover-page-elts/605-53-man/605-53-man-testcase.xml': 3.059,
    '624-rendering/08-merged-columns/gd/08-merged-columns-gd-testcase.xml': 3.105,
    '605-instance-syntax/605-16-html-limited/605-16-html-limited-testcase.xml': 3.218,
    '525-ix-syntax/ned/09-footnote/09-footnote-ned-testcase.xml': 3.237,
    '605-instance-syntax/605-24-registrant-name-matches-dei/605-24-man/605-24-registrant-name-matches-dei-man-testcase.xml': 3.334,
    '626-rendering-syntax/626-02-instant-without-matching-duration/626-02-instant-without-matching-duration-testcase.xml': 3.365,
    '525-ix-syntax/ned/07-continuation/07-continuation-ned-testcase.xml': 3.398,
    '525-ix-syntax/ned/12-references/12-references-ned-testcase.xml': 3.421,
    '616-definition-syntax/616-04-domain-member-no-cycles/616-04-domain-member-no-cycles-testcase.xml': 3.429,
    '525-ix-syntax/ned/04-nonnumeric/04-nonnumeric-ned-testcase.xml': 3.49,
    '610-label-syntax/610-09-nonnumeric-label-role/610-09-nonnumeric-label-testcase.xml': 3.549,
    '605-instance-syntax/605-43-signs/605-43-signs-testcase.xml': 3.836,
    '626-rendering-syntax/626-01-all-facts-filtered/626-01-all-facts-filtered-testcase.xml': 3.865,
    '614-calculation-syntax/614-06-cef-calculation-link-validations/614-06-cef-calculation-link-validations-testcase.xml': 4.155,
    '624-rendering/15-equity-changes/gd/15-equity-changes-gd-testcase.xml': 4.156,
    '605-instance-syntax/605-52-form-8-k-cover-page-and-name-changes-elts/605-52-man/605-52-man-testcase.xml': 4.177,
    '605-instance-syntax/605-41-seriesid/605-41-seriesid-testcase.xml': 4.315,
    '609-linkbase-syntax/609-03-no-ineffectual-arcs/609-03-no-ineffectual-arcs-testcase.xml': 4.432,
    '604-filing-semantics/604-03-xbrl-valid/604-03-xbrl-valid-testcase.xml': 4.455,
    '525-ix-syntax/efm/02-transform/02-transform-efm-testcase.xml': 4.523,
    '614-calculation-syntax/614-08-ecd-calculation-link-validations/614-08-ecd-calculation-link-validations-testcase.xml': 4.72,
    '525-ix-syntax/efm/23-rr/23-rr-efm-testcase.xml': 5.018,
    '614-calculation-syntax/614-09-OEF-calculation-link-validations/614-09-OEF-calculation-link-validations-testcase.xml': 5.078,
    '525-ix-syntax/ned/03-nonfraction/03-nonfraction-ned-testcase.xml': 6.318,
    '624-rendering/06-layout/gd/06-layout-gd-testcase.xml': 6.406,
    '624-rendering/19-nonnumeric/gd/19-nonnumeric-gd-testcase.xml': 7.381,
    '626-rendering-syntax/626-05-embedding-missing-rows-or-columns/626-05-embedding-missing-rows-or-columns-testcase.xml': 7.983,
    '525-ix-syntax/efm/19-multiio/19-multiio-efm-testcase.xml': 8.56,
    '616-definition-syntax/616-13-OEF-definition-link-validations/616-13-OEF-definition-link-validations-testcase.xml': 9.537,
    '612-presentation-syntax/612-10-cef-presentation-link-validations/612-10-cef-presentation-link-validations-testcase.xml': 9.842,
    '902-sdr/efm/62421-sdr-multiple/62421-sdr-multiple-testcase.xml': 9.996,
    '624-rendering/07-member-ordering/gd/07-member-ordering-gd-testcase.xml': 10.677,
    '605-instance-syntax/605-42-deprecated/605-42-deprecated-testcase.xml': 10.691,
    '616-definition-syntax/616-12-ecd-definition-link-validations/616-12-ecd-definition-link-validations-testcase.xml': 11.042,
    '616-definition-syntax/616-14-RXP-definition-link-validations/616-14-RXP-definition-link-validations-testcase.xml': 11.328,
    '605-instance-syntax/605-58-Resource-Extraction-Payments-Form-SD-Exhibit-201/605-58-Resource-Extraction-Payments-Form-SD-Exhibit-201-testcase.xml': 11.445,
    '626-rendering-syntax/626-04-embedding-command-syntax/626-04-embedding-command-syntax-testcase.xml': 11.509,
    '605-instance-syntax/605-50-form-20-f-cover-page-elts/605-50-man/605-50-man-testcase.xml': 12.368,
    '616-definition-syntax/616-10-cef-definition-link-validations/616-10-cef-definition-link-validations-testcase.xml': 12.622,
    '525-ix-syntax/efm/11-hidden/11-hidden-efm-testcase.xml': 13.661,
    '605-instance-syntax/605-35-numeric-units/605-35-numeric-units-testcase.xml': 15.702,
    '525-ix-syntax/efm/00-filing/00-filing-efm-testcase.xml': 17.517,
    '605-instance-syntax/605-56-prospectus-document-types/605-56-prospectus-document-types-testcase.xml': 18.927,
    '902-sdr/efm/60524-sdr-registrant-name/60524-sdr-registrant-name-testcase.xml': 21.588,
    '605-instance-syntax/605-48-cover-page-principal-office-elts/605-48-man/605-48-man-testcase.xml': 22.171,
    '525-ix-syntax/efm/22-forms/22-forms-efm-testcase.xml': 24.347,
    '622-only-supported-locations/622-01-all-supported-locations/622-01-all-supported-locations-testcase.xml': 26.323,
    '605-instance-syntax/605-26-common-shares-outstanding/605-26-man/605-26-man-testcase.xml': 32.665,
    '605-instance-syntax/605-47-company-id-cover-page-elts/605-47-man/605-47-man-testcase.xml': 34.441,
    '605-instance-syntax/605-40-submission-header/605-40-man/605-40-submission-header-man-testcase.xml': 40.013,
    '605-instance-syntax/605-57-N-1A-Fund-Shareholder-Reports/605-57-N-1A-Fund-Shareholder-Reports-testcase.xml': 40.85,
    '605-instance-syntax/605-24-registrant-name-matches-dei/605-24-gen/605-24-gen-testcase.xml': 45.88,
    '902-sdr/efm/60302-sdr-doctype/60302-sdr-doctype-testcase.xml': 46.989,
    '622-only-supported-locations/622-02-no-unsupported-locations/622-02-no-unsupported-locations-testcase.xml': 50.479,
    '605-instance-syntax/605-51-business-contact-etls/605-51-man/605-51-man-testcase.xml': 52.355,
    '605-instance-syntax/605-54-auditor-information/605-54-auditor-information-testcase.xml': 53.621,
    '605-instance-syntax/605-24-registrant-name-matches-dei/605-24-man1/605-24-man-testcase.xml': 57.21,
    '622-only-supported-locations/622-03-consistent-locations/622-03-consistent-locations-testcase.xml': 61.31,
    '605-instance-syntax/605-55-cover-page-form-N-2/605-55-cover-page-form-N-2-testcase.xml': 71.872,
    '605-instance-syntax/605-46-registered-securities-cover-page-elts/605-46-man/605-46-man-testcase.xml': 77.039,
    '605-instance-syntax/605-26-common-shares-outstanding/605-26-gen/605-26-gen-testcase.xml': 83.927,
    '605-instance-syntax/605-26-common-shares-outstanding/605-26-gen1/605-26-common-shares-outstanding-gen-testcase.xml': 86.128,
    '605-instance-syntax/605-49-cover-page-etls-and-sub-type/605-49-man/605-49-man-testcase.xml': 102.838,
    '605-instance-syntax/605-40-submission-header/605-40-man1/605-40-man-testcase.xml': 139.814,
    '605-instance-syntax/605-50-form-20-f-cover-page-elts/605-50-gen/605-50-gen-testcase.xml': 144.794,
    '605-instance-syntax/605-21-required-entity-elts/605-21-man/605-21-man-testcase.xml': 145.703,
    '605-instance-syntax/605-47-company-id-cover-page-elts/605-47-gen/605-47-gen-testcase.xml': 166.157,
    '605-instance-syntax/605-20-required-document-elts/605-20-man/605-20-man-testcase.xml': 214.467,
    '605-instance-syntax/605-46-registered-securities-cover-page-elts/605-46-gen/605-46-gen-testcase.xml': 254.546,
    '605-instance-syntax/605-52-form-8-k-cover-page-and-name-changes-elts/605-52-gen/605-52-gen-testcase.xml': 272.805,
    '605-instance-syntax/605-53-former-address-cover-page-elts/605-53-gen/605-53-gen-testcase.xml': 316.317,
    '605-instance-syntax/605-40-submission-header/605-40-gen/605-40-gen-testcase.xml': 332.685,
    '605-instance-syntax/605-48-cover-page-principal-office-elts/605-48-gen/605-48-gen-testcase.xml': 376.49,
    '605-instance-syntax/605-51-business-contact-etls/605-51-gen/605-51-gen-testcase.xml': 404.472,
    '605-instance-syntax/605-21-required-entity-elts/605-21-gen/605-21-gen-testcase.xml': 437.179,
    '605-instance-syntax/605-20-required-document-elts/605-20-gen/605-20-gen-testcase.xml': 447.472,
    '605-instance-syntax/605-49-cover-page-etls-and-sub-type/605-49-gen/605-49-gen-testcase.xml': 531.832,
}.items()}

config = ConformanceSuiteConfig(
    additional_plugins_by_prefix=[
        ('conf/612-presentation-syntax/612-09-presented-units-order', frozenset({'EdgarRenderer'})),
        ('conf/626-rendering-syntax', frozenset({'EdgarRenderer'})),
    ],
    approximate_relative_timing=TIMING,
    args=[
        '--disclosureSystem', 'efm-pragmatic',
        '--formula', 'run',
    ],
    expected_empty_testcases=frozenset(f'conf/{s}' for s in [
        '605-instance-syntax/605-45-cover-page-facts-general-case/605-45-cover-page-facts-general-case-testcase.xml',
        '609-linkbase-syntax/609-10-general-namespace-specific-custom-arc-restrictions/609-10-general-namespace-specific-custom-arc-restrictions-testcase.xml',
        '624-rendering/09-start-end-labels/gd/09-start-end-labels-gd-testcase.xml',
        '624-rendering/14-cash-flows/gd/14-cash-flows-gd-testcase.xml',
        '624-rendering/15-equity-changes/gw/15-equity-changes-gw-testcase.xml',
        '624-rendering/18-numeric/gd/18-numeric-gd-testcase.xml',
        '626-rendering-syntax/626-03-no-matching-durations/626-03-no-matching-durations-testcase.xml',
    ]),
    file='conf/testcases.xml',
    info_url='https://www.sec.gov/structureddata/osdinteractivedatatestsuite',
    local_filepath='efm-67d-230901.zip',
    name=PurePath(__file__).stem,
    plugins=frozenset({'validate/EFM', 'inlineXbrlDocumentSet'}),
    public_download_url='https://www.sec.gov/files/edgar/efm-67d-230901.zip',
    shards=20,
)
