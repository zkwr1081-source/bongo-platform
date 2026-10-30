import tempfile
import unittest
from pathlib import Path
from factory.discovery_engine import DiscoveryStore, validate_evidence

BASE = {
 "title":"Water stress signal","source_name":"Test authority","source_url":"https://example.org/report",
 "excerpt":"Observed regional water stress","domain":"water","claim_type":"observed_fact","geography":"Global",
 "license":"CC BY 4.0","published_at":"2026-10-01"
}
class DiscoveryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.store=DiscoveryStore(Path(self.tmp.name)/"test.db")
 def tearDown(self): self.tmp.cleanup()
 def test_add_and_deduplicate(self):
  first, created=self.store.add_evidence(BASE)
  second, created_again=self.store.add_evidence(BASE)
  self.assertTrue(created); self.assertFalse(created_again); self.assertEqual(first,second)
  self.assertEqual(self.store.count(),1)
 def test_reject_unknown_domain(self):
  item={**BASE,"domain":"made_up"}
  with self.assertRaises(ValueError): validate_evidence(item)
 def test_reject_missing_license_is_not_silent(self):
  item={k:v for k,v in BASE.items() if k!="license"}
  # Missing license is explicitly recorded as unspecified, not fabricated.
  self.store.add_evidence(item)
  self.assertEqual(self.store.list_evidence()[0]["license"],"unspecified")
 def test_score_penalizes_risk_and_links_evidence(self):
  eid,_=self.store.add_evidence(BASE)
  scores={k:4 for k in ("urgency","reach","evidence_quality","gap","feasibility","time_to_impact")}
  scores.update(safety_risk=0,privacy_risk=0,environmental_risk=0)
  self.store.add_opportunity({"title":"Leak detection","problem":"Water loss","proposal":"Prioritize repair signals","evidence_ids":[eid],"scores":scores})
  self.assertEqual(self.store.list_opportunities()[0]["total_score"],4.0)
 def test_reject_unknown_evidence_reference(self):
  scores={k:3 for k in ("urgency","reach","evidence_quality","gap","feasibility","time_to_impact","safety_risk","privacy_risk","environmental_risk")}
  with self.assertRaises(ValueError):
   self.store.add_opportunity({"title":"x","problem":"p","proposal":"q","evidence_ids":[999],"scores":scores})
if __name__=="__main__": unittest.main()
