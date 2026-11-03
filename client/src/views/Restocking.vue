<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budgetLabel') }}</h3>
          <span class="budget-max">{{ t('restocking.budgetMax', { amount: formatMoney(maxBudget) }) }}</span>
        </div>
        <div class="budget-control">
          <div class="budget-value">{{ formatMoney(budget) }}</div>
          <input
            v-model.number="budget"
            type="range"
            class="budget-slider"
            min="0"
            :max="sliderMax"
            step="50"
            :aria-label="t('restocking.budgetLabel')"
          />
          <div class="budget-scale">
            <span>{{ formatMoney(0) }}</span>
            <span>{{ formatMoney(sliderMax) }}</span>
          </div>
        </div>
      </div>

      <div class="stats-grid">
        <div :class="['stat-card', isOverBudget ? 'danger' : 'info']">
          <div class="stat-label">{{ t('restocking.selectedTotal') }}</div>
          <div class="stat-value">{{ formatMoney(selectedTotal) }}</div>
          <div class="stat-sub">{{ t('restocking.ofBudget', { amount: formatMoney(budget) }) }}</div>
        </div>
        <div :class="['stat-card', remainingBudget < 0 ? 'danger' : 'success']">
          <div class="stat-label">{{ t('restocking.remaining') }}</div>
          <div class="stat-value">{{ formatMoney(remainingBudget) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.leadTime') }}</div>
          <div class="stat-value">{{ t('restocking.days', { count: orderLeadTime }) }}</div>
        </div>
      </div>

      <div v-if="isOverBudget" class="error">
        {{ t('restocking.overBudget', { amount: formatMoney(selectedTotal - budget) }) }}
      </div>
      <div v-if="recError" class="error">{{ recError }}</div>
      <div v-if="orderError" class="error">{{ orderError }}</div>
      <div v-if="lastOrder" class="success-message">
        {{ t('restocking.success', { orderNumber: lastOrder.order_number }) }}
        <router-link to="/orders" class="success-link">{{ t('restocking.viewOrders') }}</router-link>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendationsTitle') }} ({{ rows.length }})</h3>
          <button
            type="button"
            class="place-order-button"
            :disabled="!canPlaceOrder"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="rows.length === 0" class="empty-state">{{ t('restocking.empty') }}</div>
        <div v-else class="table-container">
          <table class="restock-table">
            <thead>
              <tr>
                <th class="col-select">{{ t('restocking.table.select') }}</th>
                <th>{{ t('restocking.table.item') }}</th>
                <th class="col-trend">{{ t('restocking.table.trend') }}</th>
                <th class="col-num">{{ t('restocking.table.gap') }}</th>
                <th class="col-num">{{ t('restocking.table.unitCost') }}</th>
                <th class="col-qty">{{ t('restocking.table.quantity') }}</th>
                <th class="col-num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="col-lead">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.sku" :class="{ 'row-deselected': !row.selected }">
                <td class="col-select">
                  <input v-model="row.selected" type="checkbox" :aria-label="row.sku" />
                </td>
                <td>
                  <div class="item-name">{{ translateProductName(row.name) }}</div>
                  <div class="item-sku">{{ row.sku }}</div>
                </td>
                <td class="col-trend">
                  <span :class="['badge', row.trend]">{{ t(`trends.${row.trend}`) }}</span>
                </td>
                <td class="col-num">{{ row.gap.toLocaleString() }}</td>
                <td class="col-num">{{ formatMoney(row.unit_cost) }}</td>
                <td class="col-qty">
                  <input
                    v-model.number="row.quantity"
                    type="number"
                    min="1"
                    step="1"
                    :class="['qty-input', { invalid: row.selected && !isValidQty(row.quantity) }]"
                    :disabled="!row.selected"
                  />
                </td>
                <td class="col-num"><strong>{{ formatMoney(lineTotal(row)) }}</strong></td>
                <td class="col-lead">{{ t('restocking.days', { count: row.lead_time_days }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

const BUDGET_STEP = 50
const DEBOUNCE_MS = 250

export default {
  name: 'Restocking',
  setup() {
    const { t, currentLocale, currentCurrency, translateProductName } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const loading = ref(true)
    const error = ref(null)
    const recError = ref(null)
    const budget = ref(0)
    const maxBudget = ref(0)
    const rows = ref([])
    const submitting = ref(false)
    const orderError = ref(null)
    const lastOrder = ref(null)

    // Round the slider max up to the next step so the full max_budget stays reachable with step=50
    const sliderMax = computed(() => Math.ceil(maxBudget.value / BUDGET_STEP) * BUDGET_STEP)

    const formatMoney = (value) => {
      const amount = Number.isFinite(value) ? value : 0
      const sign = amount < 0 ? '-' : ''
      // Pin to the app locale; the browser default would give e.g. "2.050,00" on a German system
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return sign + currencySymbol.value + Math.abs(amount).toLocaleString(locale, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    const isValidQty = (qty) => Number.isInteger(qty) && qty >= 1

    const lineTotal = (row) => (isValidQty(row.quantity) ? row.quantity * row.unit_cost : 0)

    const selectedRows = computed(() => rows.value.filter(row => row.selected))

    // Round to cents to avoid float drift flagging an exactly-on-budget selection as over budget
    const selectedTotal = computed(() => {
      const total = selectedRows.value.reduce((sum, row) => sum + lineTotal(row), 0)
      return Math.round(total * 100) / 100
    })

    const remainingBudget = computed(() => Math.round((budget.value - selectedTotal.value) * 100) / 100)

    const isOverBudget = computed(() => selectedTotal.value > budget.value)

    const orderLeadTime = computed(() => {
      return selectedRows.value.reduce((max, row) => Math.max(max, row.lead_time_days), 0)
    })

    const canPlaceOrder = computed(() => {
      return selectedRows.value.length > 0 &&
        selectedRows.value.every(row => isValidQty(row.quantity)) &&
        !isOverBudget.value &&
        !submitting.value
    })

    // Monotonic id so a slow earlier response cannot overwrite a newer one
    let requestId = 0

    const loadRecommendations = async () => {
      const currentRequest = ++requestId
      try {
        const data = await api.getRestockRecommendations(budget.value)
        if (currentRequest !== requestId) return
        maxBudget.value = data.max_budget
        // New recommendations replace any local edits
        rows.value = data.items.map(item => ({
          ...item,
          selected: true,
          quantity: item.recommended_qty
        }))
        recError.value = null
      } catch (err) {
        if (currentRequest !== requestId) return
        recError.value = 'Failed to load restocking recommendations: ' + err.message
      }
    }

    const init = async () => {
      try {
        loading.value = true
        // First call with budget=0 only to learn max_budget, then default to 50% of it
        const probe = await api.getRestockRecommendations(0)
        maxBudget.value = probe.max_budget
        budget.value = Math.round(probe.max_budget / 2 / BUDGET_STEP) * BUDGET_STEP
        await loadRecommendations()
        error.value = recError.value
      } catch (err) {
        error.value = 'Failed to load restocking recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    let debounceTimer = null

    watch(budget, () => {
      if (loading.value) return
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(loadRecommendations, DEBOUNCE_MS)
    })

    const placeOrder = async () => {
      if (!canPlaceOrder.value) return
      submitting.value = true
      orderError.value = null
      lastOrder.value = null
      try {
        const order = await api.createRestockOrder({
          budget: budget.value,
          items: selectedRows.value.map(row => ({ sku: row.sku, quantity: row.quantity }))
        })
        lastOrder.value = order
        await loadRecommendations()
      } catch (err) {
        orderError.value = err.response?.data?.detail || `${t('restocking.orderFailed')}: ${err.message}`
      } finally {
        submitting.value = false
      }
    }

    onMounted(init)
    onBeforeUnmount(() => clearTimeout(debounceTimer))

    return {
      t,
      translateProductName,
      loading,
      error,
      recError,
      budget,
      maxBudget,
      sliderMax,
      rows,
      submitting,
      orderError,
      lastOrder,
      selectedTotal,
      remainingBudget,
      isOverBudget,
      orderLeadTime,
      canPlaceOrder,
      formatMoney,
      isValidQty,
      lineTotal,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-max {
  color: #68646f;
  font-size: 0.875rem;
}

.budget-control {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.budget-value {
  font-size: 2rem;
  font-weight: 700;
  color: #0a0011;
  letter-spacing: -0.025em;
}

.budget-slider {
  width: 100%;
  accent-color: #a100ff;
  cursor: pointer;
}

.budget-scale {
  display: flex;
  justify-content: space-between;
  color: #68646f;
  font-size: 0.813rem;
}

.stat-sub {
  margin-top: 0.25rem;
  color: #68646f;
  font-size: 0.813rem;
}

.success-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #0b7a4b;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  font-size: 0.938rem;
}

.success-link {
  color: #047857;
  font-weight: 600;
}

.place-order-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #a100ff;
  color: white;
  font-size: 0.813rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.place-order-button:hover:not(:disabled) {
  background: #7500c0;
}

.place-order-button:disabled {
  background: #cfcfcf;
  color: #68646f;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #68646f;
  font-size: 0.938rem;
}

.col-select {
  width: 70px;
}

.col-trend {
  width: 130px;
}

.col-num {
  width: 120px;
  text-align: right;
}

.col-qty {
  width: 110px;
}

.col-lead {
  width: 100px;
}

.item-name {
  font-weight: 500;
  color: #0a0011;
}

.item-sku {
  font-size: 0.75rem;
  color: #68646f;
}

.qty-input {
  width: 90px;
  padding: 0.313rem 0.5rem;
  border: 1px solid #e4e4e1;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #0a0011;
}

.qty-input:focus {
  outline: none;
  border-color: #a100ff;
}

.qty-input.invalid {
  border-color: #c4122f;
}

.qty-input:disabled {
  background: #f7f7f5;
  color: #8f8b96;
}

.row-deselected td {
  color: #8f8b96;
}
</style>
