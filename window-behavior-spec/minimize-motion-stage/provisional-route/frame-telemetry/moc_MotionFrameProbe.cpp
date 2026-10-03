/****************************************************************************
** Meta object code from reading C++ file 'MotionFrameProbe.hpp'
**
** Created by: The Qt Meta Object Compiler version 69 (Qt 6.11.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "MotionFrameProbe.hpp"
#include <QtCore/qmetatype.h>

#include <QtCore/qtmochelpers.h>

#include <memory>


#include <QtCore/qxptype_traits.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'MotionFrameProbe.hpp' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 69
#error "This file was generated using the moc from 6.11.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

#ifndef Q_CONSTINIT
#define Q_CONSTINIT
#endif

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
QT_WARNING_DISABLE_GCC("-Wuseless-cast")
namespace {
struct qt_meta_tag_ZN16MotionFrameProbeE_t {};
} // unnamed namespace

template <> constexpr inline auto MotionFrameProbe::qt_create_metaobjectdata<qt_meta_tag_ZN16MotionFrameProbeE_t>()
{
    namespace QMC = QtMocConstants;
    QtMocHelpers::StringRefStorage qt_stringData {
        "MotionFrameProbe",
        "frameDataChanged",
        "",
        "observedItemChanged",
        "framesAfter",
        "QVariantList",
        "sequence",
        "frameData",
        "QVariantMap",
        "observedItem",
        "QQuickItem*"
    };

    QtMocHelpers::UintData qt_methods {
        // Signal 'frameDataChanged'
        QtMocHelpers::SignalData<void()>(1, 2, QMC::AccessPublic, QMetaType::Void),
        // Signal 'observedItemChanged'
        QtMocHelpers::SignalData<void()>(3, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'framesAfter'
        QtMocHelpers::MethodData<QVariantList(quint64) const>(4, 2, QMC::AccessPublic, 0x80000000 | 5, {{
            { QMetaType::ULongLong, 6 },
        }}),
        // Method 'framesAfter'
        QtMocHelpers::MethodData<QVariantList() const>(4, 2, QMC::AccessPublic | QMC::MethodCloned, 0x80000000 | 5),
    };
    QtMocHelpers::UintData qt_properties {
        // property 'frameData'
        QtMocHelpers::PropertyData<QVariantMap>(7, 0x80000000 | 8, QMC::DefaultPropertyFlags | QMC::Writable | QMC::EnumOrFlag | QMC::StdCppSet, 0),
        // property 'observedItem'
        QtMocHelpers::PropertyData<QQuickItem*>(9, 0x80000000 | 10, QMC::DefaultPropertyFlags | QMC::Writable | QMC::EnumOrFlag | QMC::StdCppSet, 1),
    };
    QtMocHelpers::UintData qt_enums {
    };
    return QtMocHelpers::metaObjectData<MotionFrameProbe, qt_meta_tag_ZN16MotionFrameProbeE_t>(QMC::MetaObjectFlag{}, qt_stringData,
            qt_methods, qt_properties, qt_enums);
}
Q_CONSTINIT const QMetaObject MotionFrameProbe::staticMetaObject = { {
    QMetaObject::SuperData::link<QQuickItem::staticMetaObject>(),
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN16MotionFrameProbeE_t>.stringdata,
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN16MotionFrameProbeE_t>.data,
    qt_static_metacall,
    nullptr,
    qt_staticMetaObjectRelocatingContent<qt_meta_tag_ZN16MotionFrameProbeE_t>.metaTypes,
    nullptr
} };

void MotionFrameProbe::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    auto *_t = static_cast<MotionFrameProbe *>(_o);
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: _t->frameDataChanged(); break;
        case 1: _t->observedItemChanged(); break;
        case 2: { QVariantList _r = _t->framesAfter((*reinterpret_cast<std::add_pointer_t<quint64>>(_a[1])));
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        case 3: { QVariantList _r = _t->framesAfter();
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        default: ;
        }
    }
    if (_c == QMetaObject::IndexOfMethod) {
        if (QtMocHelpers::indexOfMethod<void (MotionFrameProbe::*)()>(_a, &MotionFrameProbe::frameDataChanged, 0))
            return;
        if (QtMocHelpers::indexOfMethod<void (MotionFrameProbe::*)()>(_a, &MotionFrameProbe::observedItemChanged, 1))
            return;
    }
    if (_c == QMetaObject::RegisterPropertyMetaType) {
        switch (_id) {
        default: *reinterpret_cast<int*>(_a[0]) = -1; break;
        case 1:
            *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< QQuickItem* >(); break;
        }
    }
    if (_c == QMetaObject::ReadProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 0: *reinterpret_cast<QVariantMap*>(_v) = _t->frameData(); break;
        case 1: *reinterpret_cast<QQuickItem**>(_v) = _t->observedItem(); break;
        default: break;
        }
    }
    if (_c == QMetaObject::WriteProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 0: _t->setFrameData(*reinterpret_cast<QVariantMap*>(_v)); break;
        case 1: _t->setObservedItem(*reinterpret_cast<QQuickItem**>(_v)); break;
        default: break;
        }
    }
}

const QMetaObject *MotionFrameProbe::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *MotionFrameProbe::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_staticMetaObjectStaticContent<qt_meta_tag_ZN16MotionFrameProbeE_t>.strings))
        return static_cast<void*>(this);
    return QQuickItem::qt_metacast(_clname);
}

int MotionFrameProbe::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QQuickItem::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 4)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 4;
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 4)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 4;
    }
    if (_c == QMetaObject::ReadProperty || _c == QMetaObject::WriteProperty
            || _c == QMetaObject::ResetProperty || _c == QMetaObject::BindableProperty
            || _c == QMetaObject::RegisterPropertyMetaType) {
        qt_static_metacall(this, _c, _id, _a);
        _id -= 2;
    }
    return _id;
}

// SIGNAL 0
void MotionFrameProbe::frameDataChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void MotionFrameProbe::observedItemChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}
QT_WARNING_POP
