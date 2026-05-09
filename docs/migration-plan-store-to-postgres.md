# Migration Plan: Incremental Store-to-Postgres Migration

## Overview

This document outlines the phased migration from in-memory stores to PostgreSQL-backed persistence while maintaining system stability and providing rollback capabilities.

## Current Volatile State Inventory

### Production Domain
- **Location**: `backend/domain/production/services.py`
- **Store**: `_productions_store` (dict-based in-memory storage)
- **Data**: Production aggregates, workflow state, input snapshots
- **Impact**: Complete production lifecycle lost on restart

### Composition Domain
- **Location**: `backend/domain/composition/services.py`
- **Store**: `_composition_store` (dict-based in-memory storage)
- **Data**: Compositions, composition slots, template-specific outputs
- **Impact**: Composition previews and render inputs lost on restart

### Render Domain
- **Location**: `backend/domain/render/services.py`
- **Store**: `RenderJobStore` class (in-memory job tracking)
- **Data**: Render job status, provider responses, output URLs
- **Impact**: Active render progress and results lost on restart

### Review Domain
- **Location**: `backend/domain/human_review/` (services and models)
- **Store**: Various in-memory structures for queue state
- **Data**: Review items, scoring results, decision history
- **Impact**: Review decisions and audit trail lost on restart

## Migration Phases

### Phase 1: Production Core Persistence (Story 7.4)
**Scope**: Replace `_productions_store` with PostgreSQL persistence
**Tables**: `productions`, `productions_history`
**Endpoints**: `/api/v1/productions/*`
**Rollback**: Toggle feature flag to revert to in-memory store

**Verification Gates**:
- All production CRUD operations work against database
- State transitions persist across restarts
- Aggregate business rules remain intact
- Performance benchmarks meet requirements

### Phase 2: Review Queue & Decision Chain (Story 7.5)
**Scope**: Persist review items, scoring, and decisions
**Tables**: `review_queues`, `review_items`, `review_items_history`, `scoring_results`
**Endpoints**: `/api/v1/review/*`
**Dependencies**: Phase 1 complete

**Verification Gates**:
- Review queue survives restarts
- Scoring results persist
- Decision history is complete
- UI contract remains stable

### Phase 3: Composition & Render Persistence (Story 7.5)
**Scope**: Replace `_composition_store` and `RenderJobStore`
**Tables**: `compositions`, `compositions_history`, `renders`, `renders_history`
**Endpoints**: `/api/v1/renders/*`, `/api/v1/compositions/*`
**Dependencies**: Phase 1 complete

**Verification Gates**:
- Composition previews persist
- Render job progress survives restarts
- Output URLs and status are preserved
- External provider callbacks work

## Coexistence Strategy

During migration, maintain dual storage:

1. **Write to Both**: New data written to both in-memory and database
2. **Read from Database**: Routes read from database, fall back to memory if needed
3. **Validation**: Compare results between stores during transition
4. **Gradual Cutover**: Feature flags control which store is authoritative

## Rollback Plan

### Per-Phase Rollback
Each phase includes:

1. **Feature Flag Reversal**: Toggle to use in-memory store
2. **Data Export**: Export database data to reconstruct memory state
3. **Verification**: Confirm system returns to pre-migration behavior
4. **Documentation**: Update operational runbooks

### Emergency Rollback
- **Trigger**: Critical issues preventing operation
- **Process**: Feature flag flip + data reconstruction
- **Timeline**: < 30 minutes to complete
- **Verification**: Full system functionality restored

## Migration Execution Checklist

### Phase 1 Preparation
- [ ] Database schema deployed to staging
- [ ] Repository interfaces implemented
- [ ] Feature flag infrastructure ready
- [ ] Data migration scripts tested
- [ ] Rollback procedures documented

### Phase 1 Execution
- [ ] Deploy with feature flag OFF (memory store active)
- [ ] Enable dual-write mode
- [ ] Monitor for data consistency issues
- [ ] Validate read operations from database
- [ ] Toggle feature flag ON (database authoritative)
- [ ] Disable memory store cleanup

### Phase 1 Verification
- [ ] All production endpoints tested
- [ ] Restart survivability confirmed
- [ ] Performance within acceptable ranges
- [ ] Business rule compliance verified

## Risk Mitigation

### Data Integrity Risks
- **Mitigation**: Dual-write validation, checksum comparison
- **Detection**: Automated consistency checks
- **Recovery**: Reconstruct from audit logs

### Performance Risks
- **Mitigation**: Database indexing, query optimization
- **Detection**: Performance monitoring alerts
- **Recovery**: Query optimization, read replicas

### Operational Risks
- **Mitigation**: Gradual rollout, feature flags
- **Detection**: Health checks, error monitoring
- **Recovery**: Immediate rollback capability

## Success Criteria

- Zero data loss during migration
- No downtime required
- Performance degradation < 10%
- Full rollback capability maintained
- All verification gates passed

## Timeline

- **Phase 1**: 1-2 weeks (Story 7.4)
- **Phase 2**: 2-3 weeks (Story 7.5 - review portion)
- **Phase 3**: 2-3 weeks (Story 7.5 - composition/render portion)
- **Total Migration**: 5-8 weeks with safety buffers

## Dependencies

- PostgreSQL 16+ infrastructure ready
- Database connection pooling configured
- Monitoring and alerting in place
- Team availability for phased rollout</content>
<parameter name="filePath">docs/stories/7.10.migration-plan.md