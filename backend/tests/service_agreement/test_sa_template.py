from squid_py.service_agreement.utils import get_sla_template_dict, get_sla_template_path


def test_setup_service_agreement_template(publisher_ocean_instance):
    template_dict = get_sla_template_dict(get_sla_template_path())
    tx_receipt = publisher_ocean_instance._register_service_agreement_template(template_dict, publisher_ocean_instance.main_account)

    # verify new sa template is registered

