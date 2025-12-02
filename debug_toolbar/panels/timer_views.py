import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.translation import gettext as _

from debug_toolbar._compat import login_not_required
from debug_toolbar.decorators import render_with_toolbar_language, require_show_toolbar
from debug_toolbar.toolbar import DebugToolbar


@login_not_required
@require_show_toolbar
@render_with_toolbar_language
def timer_export(request):
    """Return a structured JSON export of the Timer panel stats."""
    from debug_toolbar.panels.timer import TimerPanel

    request_id = request.GET.get("request_id")
    if not request_id:
        return HttpResponseBadRequest(
            _("The 'request_id' query parameter is required.")
        )

    browser_timing_raw = request.GET.get("browser_timing")
    browser_timing = None
    if browser_timing_raw:
        try:
            browser_timing = json.loads(browser_timing_raw)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(_("Invalid browser timing payload."))

    toolbar = DebugToolbar.fetch(request_id, TimerPanel.panel_id)
    if toolbar is None:
        content = _(
            "Data for this panel isn't available anymore. "
            "Please reload the page and retry."
        )
        return HttpResponseBadRequest(content)

    panel = toolbar.get_panel_by_id(TimerPanel.panel_id)
    payload = panel.get_export_data()
    payload["browser_timing"] = browser_timing

    response = JsonResponse(payload, json_dumps_params={"indent": 2})
    response["Content-Disposition"] = (
        f'attachment; filename="djdt-timer-{request_id}.json"'
    )
    return response
