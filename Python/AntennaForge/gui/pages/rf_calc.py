"""
RF Calculator Page — EIRP, Link Budget, Power Density.
"""

import threading
import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import (
    ScrollablePage, Card, SectionHeading, ActionButton,
    LabeledEntry, LabeledOption, FilePicker, ResultBox, Tooltip,
)


class RFCalcPage(ScrollablePage):
    """RF calculator page for EIRP, power density, FSPL, and link budget."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._build()

    def _build(self) -> None:
        SectionHeading(self, text="RF Calculations").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self, text="EIRP, power density, free-space path loss, and link budget analysis.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # ════════════════════════════════════════════════════════
        #  EIRP CALCULATOR
        # ════════════════════════════════════════════════════════
        eirp = Card(self, title="EIRP Calculator")
        eirp.pack(fill="x", padx=24, pady=8)

        e_inner = ctk.CTkFrame(eirp, fg_color="transparent")
        e_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_eirp_file = FilePicker(e_inner, "Pattern CSV")
        self.w_eirp_file.pack(fill="x", pady=4)

        self.w_tx_power = LabeledEntry(e_inner, "Tx Power (dBm)", "30.0",
                                       tooltip="Transmit power in dBm")
        self.w_tx_power.pack(fill="x", pady=4)

        self.w_cable_loss = LabeledEntry(e_inner, "Cable Loss (dB)", "2.0")
        self.w_cable_loss.pack(fill="x", pady=4)

        btn_row = ctk.CTkFrame(e_inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(8, 4))

        ActionButton(
            btn_row, text="📐  Calculate EIRP", width=200,
            command=self._on_eirp,
        ).pack(side="left")

        ActionButton(
            btn_row, text="Calculate Power Density", width=220,
            style="secondary", command=self._on_power_density,
        ).pack(side="left", padx=(12, 0))

        self.w_pd_dist = LabeledEntry(e_inner, "Distance (m)", "1000.0",
                                      tooltip="For power density calculation")
        self.w_pd_dist.pack(fill="x", pady=4)

        self.eirp_result = ResultBox(self, height=140)
        self.eirp_result.pack(fill="x", padx=24, pady=(0, 16))

        # ════════════════════════════════════════════════════════
        #  FSPL QUICK CALC
        # ════════════════════════════════════════════════════════
        fspl = Card(self, title="Free-Space Path Loss")
        fspl.pack(fill="x", padx=24, pady=8)

        f_inner = ctk.CTkFrame(fspl, fg_color="transparent")
        f_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_fspl_dist = LabeledEntry(f_inner, "Distance (km)", "100.0")
        self.w_fspl_dist.pack(fill="x", pady=4)

        self.w_fspl_freq = LabeledEntry(f_inner, "Frequency (MHz)", "1000.0")
        self.w_fspl_freq.pack(fill="x", pady=4)

        ActionButton(
            f_inner, text="Calculate FSPL", width=180,
            command=self._on_fspl,
        ).pack(anchor="w", pady=(8, 4))

        self.fspl_result = ResultBox(self, height=60)
        self.fspl_result.pack(fill="x", padx=24, pady=(0, 16))

        # ════════════════════════════════════════════════════════
        #  LINK BUDGET
        # ════════════════════════════════════════════════════════
        lb = Card(self, title="Link Budget Analysis")
        lb.pack(fill="x", padx=24, pady=8)

        l_inner = ctk.CTkFrame(lb, fg_color="transparent")
        l_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_lb_mode = LabeledOption(
            l_inner, "Mode",
            ["Boresight Link Margin", "Full Angular Map"],
            default="Boresight Link Margin",
        )
        self.w_lb_mode.pack(fill="x", pady=4)

        self.w_lb_tx = FilePicker(l_inner, "Tx Pattern CSV")
        self.w_lb_tx.pack(fill="x", pady=4)

        self.w_lb_rx = FilePicker(l_inner, "Rx Pattern CSV")
        self.w_lb_rx.pack(fill="x", pady=4)

        self.w_lb_dist = LabeledEntry(l_inner, "Distance (km)", "100.0")
        self.w_lb_dist.pack(fill="x", pady=4)

        self.w_lb_freq = LabeledEntry(l_inner, "Frequency (MHz)", "1000.0")
        self.w_lb_freq.pack(fill="x", pady=4)

        self.w_lb_txpwr = LabeledEntry(l_inner, "Tx Power (dBm)", "30.0")
        self.w_lb_txpwr.pack(fill="x", pady=4)

        self.w_lb_txloss = LabeledEntry(l_inner, "Tx Cable Loss (dB)", "2.0")
        self.w_lb_txloss.pack(fill="x", pady=4)

        self.w_lb_rxloss = LabeledEntry(l_inner, "Rx Cable Loss (dB)", "1.0")
        self.w_lb_rxloss.pack(fill="x", pady=4)

        self.w_lb_sens = LabeledEntry(
            l_inner, "Rx Sensitivity (dBm)", "-90.0",
            tooltip="Only for boresight link margin mode")
        self.w_lb_sens.pack(fill="x", pady=4)

        ActionButton(
            l_inner, text="📡  Calculate Link Budget", width=240,
            command=self._on_link_budget,
        ).pack(anchor="w", pady=(8, 4))

        self.lb_result = ResultBox(self, height=220)
        self.lb_result.pack(fill="x", padx=24, pady=(0, 24))

        # ── Tooltips ───────────────────────────────────────────
        # EIRP
        Tooltip(self.w_eirp_file,
                "Antenna pattern CSV for EIRP calculation.\n"
                "Gain values at every az/el point are combined with "
                "Tx power and cable loss to compute EIRP = Ptx − Loss + Gain.\n"
                "Output: a new CSV with EIRP in dBm at every angle.")
        Tooltip(self.w_tx_power,
                "Transmitter output power in dBm.\n"
                "This is the conducted power at the radio port, before "
                "cable loss.\n"
                "30 dBm = 1 W, 40 dBm = 10 W, 47 dBm = 50 W.")
        Tooltip(self.w_cable_loss,
                "Feed-line attenuation between transmitter and antenna (dB).\n"
                "Includes coaxial cable, connectors, lightning arrestors, "
                "and any jumper losses.\n"
                "Typical: 1–3 dB for short runs, 5–10 dB for long runs\n"
                "at microwave frequencies.")
        Tooltip(self.w_pd_dist,
                "Distance from the antenna in metres for power density.\n"
                "Power density (W/m²) = EIRP / (4π d²).\n"
                "Common use: MPE/RF safety compliance distance checks.\n"
                "1000 m is a typical starting point for telecom sites.")

        # FSPL
        Tooltip(self.w_fspl_dist,
                "Distance between transmitter and receiver in kilometres.\n"
                "Free-space path loss increases with the square of distance:\n"
                "FSPL = 20 log₁₀(d) + 20 log₁₀(f) + 32.44 dB.\n"
                "Example: 100 km at 1 GHz ≈ 132 dB.")
        Tooltip(self.w_fspl_freq,
                "Operating frequency in MHz.\n"
                "Path loss increases with the square of frequency at the "
                "same distance. Doubling the frequency adds ~6 dB of loss.\n"
                "Enter the center frequency of your link.")

        # Link budget
        Tooltip(self.w_lb_mode,
                "Link budget calculation mode:\n"
                "• Boresight Link Margin — single-point calculation at "
                "az=0°, el=0° for both antennas. Reports received power "
                "and margin above Rx sensitivity.\n"
                "• Full Angular Map — computes received power at every "
                "az/el combination using both patterns. Outputs a CSV\n"
                "and reports the best-case pointing angles.")
        Tooltip(self.w_lb_tx,
                "Transmit antenna pattern CSV.\n"
                "The gain at each angle is used to compute EIRP "
                "directionally.\n"
                "In Boresight mode, only the (0°, 0°) gain is used.")
        Tooltip(self.w_lb_rx,
                "Receive antenna pattern CSV.\n"
                "Rx gain at each angle is added to the received signal.\n"
                "In Boresight mode, only the (0°, 0°) gain is used.")
        Tooltip(self.w_lb_dist,
                "Link distance in kilometres.\n"
                "Determines the free-space path loss component.\n"
                "For short links (< 1 km), enter as a fraction (e.g. 0.5).")
        Tooltip(self.w_lb_freq,
                "Operating frequency in MHz.\n"
                "Used to compute FSPL. Must match the frequency at which "
                "the Tx and Rx patterns were generated or measured.")
        Tooltip(self.w_lb_txpwr,
                "Transmitter output power in dBm.\n"
                "Combined with Tx antenna gain and cable loss to compute "
                "EIRP.\n"
                "30 dBm = 1 W, 43 dBm = 20 W, 47 dBm = 50 W.")
        Tooltip(self.w_lb_txloss,
                "Cable / connector loss on the transmit side (dB).\n"
                "Subtracted from Tx power before antenna gain is applied.\n"
                "Include all losses between the radio and the antenna port.")
        Tooltip(self.w_lb_rxloss,
                "Cable / connector loss on the receive side (dB).\n"
                "Subtracted from the signal after the Rx antenna.\n"
                "Include all losses between the Rx antenna port and "
                "the receiver input.")
        Tooltip(self.w_lb_sens,
                "Receiver sensitivity threshold in dBm.\n"
                "The minimum detectable signal level for the receiver.\n"
                "Link margin = Rx Power − Sensitivity.\n"
                "Positive margin = link closes; negative = link fails.\n"
                "Only used in Boresight Link Margin mode.")

    # ────────────────────────────────────────────────────────────
    def _on_eirp(self) -> None:
        path = self.w_eirp_file.get()
        if not path:
            self.eirp_result.set_text("Select a pattern CSV file.")
            return

        self.app.status.busy("Calculating EIRP…")

        def work():
            try:
                from core.eirp import compute_eirp
                tx = float(self.w_tx_power.get())
                loss = float(self.w_cable_loss.get())
                out_path, peak, az, el = compute_eirp(path, tx, loss)

                lines = [
                    f"Peak EIRP:    {peak:.2f} dBm",
                    f"Peak at:      Az={az}°, El={el}°",
                    f"Tx Power:     {tx} dBm",
                    f"Cable Loss:   {loss} dB",
                    f"Output:       {out_path}",
                ]
                text = "\n".join(lines)
                self.after(0, lambda: self.eirp_result.set_text(text))
                self.after(0, lambda: self.app.status.success("EIRP calculated"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.eirp_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    def _on_power_density(self) -> None:
        path = self.w_eirp_file.get()
        if not path:
            self.eirp_result.set_text("Select a pattern CSV file.")
            return

        self.app.status.busy("Calculating power density…")

        def work():
            try:
                from core.eirp import compute_power_density
                tx = float(self.w_tx_power.get())
                loss = float(self.w_cable_loss.get())
                dist = float(self.w_pd_dist.get())
                out = compute_power_density(path, tx, loss, dist)

                text = f"Power density CSV → {out}\n" \
                       f"Distance: {dist} m  |  Tx: {tx} dBm  |  Loss: {loss} dB"
                self.after(0, lambda: self.eirp_result.set_text(text))
                self.after(0, lambda: self.app.status.success("Power density calculated"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.eirp_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    def _on_fspl(self) -> None:
        try:
            from core.link_budget import free_space_path_loss
            dist = float(self.w_fspl_dist.get())
            freq = float(self.w_fspl_freq.get())
            fspl = free_space_path_loss(dist, freq)
            self.fspl_result.set_text(
                f"FSPL = {fspl:.2f} dB  "
                f"(d={dist} km, f={freq} MHz)")
            self.app.status.success("FSPL calculated")
        except Exception as e:
            self.fspl_result.set_text(f"Error: {e}")

    def _on_link_budget(self) -> None:
        mode = self.w_lb_mode.get()
        tx_f = self.w_lb_tx.get()
        rx_f = self.w_lb_rx.get()

        if not tx_f or not rx_f:
            self.lb_result.set_text("Select both Tx and Rx pattern CSV files.")
            return

        self.app.status.busy("Calculating link budget…")

        def work():
            try:
                dist = float(self.w_lb_dist.get())
                freq = float(self.w_lb_freq.get())
                tx_pwr = float(self.w_lb_txpwr.get())
                tx_loss = float(self.w_lb_txloss.get())
                rx_loss = float(self.w_lb_rxloss.get())

                if "Boresight" in mode:
                    from core.link_budget import compute_link_margin
                    sens = float(self.w_lb_sens.get())
                    r = compute_link_margin(
                        tx_f, rx_f, dist, freq,
                        tx_power_dbm=tx_pwr,
                        rx_sensitivity_dbm=sens,
                        tx_cable_loss_db=tx_loss,
                        rx_cable_loss_db=rx_loss,
                    )

                    lines = [
                        "═══ Link Budget Summary ═══",
                        f"  Tx Power:       {r['tx_power_dbm']:.1f} dBm",
                        f"  Tx Gain:        {r['tx_gain_dbi']:.1f} dBi",
                        f"  Tx Cable Loss:  {r['tx_cable_loss_db']:.1f} dB",
                        f"  FSPL:           {r['fspl_db']:.1f} dB",
                        f"  Rx Gain:        {r['rx_gain_dbi']:.1f} dBi",
                        f"  Rx Cable Loss:  {r['rx_cable_loss_db']:.1f} dB",
                        f"  ─────────────────────────",
                        f"  Rx Power:       {r['rx_power_dbm']:.1f} dBm",
                        f"  Sensitivity:    {r['rx_sensitivity_dbm']:.1f} dBm",
                        f"  Link Margin:    {r['link_margin_db']:.1f} dB",
                    ]
                    text = "\n".join(lines)
                else:
                    from core.link_budget import compute_link_budget
                    out, peak_rx, tx_az, rx_az = compute_link_budget(
                        tx_f, rx_f, dist, freq,
                        tx_power_dbm=tx_pwr,
                        tx_cable_loss_db=tx_loss,
                        rx_cable_loss_db=rx_loss,
                    )
                    lines = [
                        f"Peak Rx Power:  {peak_rx:.1f} dBm",
                        f"Best Tx Az:     {tx_az}°",
                        f"Best Rx Az:     {rx_az}°",
                        f"Output CSV:     {out}",
                    ]
                    text = "\n".join(lines)

                self.after(0, lambda: self.lb_result.set_text(text))
                self.after(0, lambda: self.app.status.success("Link budget complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.lb_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()
